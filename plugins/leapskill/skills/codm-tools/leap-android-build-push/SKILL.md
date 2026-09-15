---
name: leap-android-build-push
description: CODM Android 引擎 so 的编译-推送-验证一条龙：分支/工作区/包版本门禁 → [Leap] 时间戳自动注入（PCHD 模板）→ Bee 编译 AndroidPlayer（增量）→ il2cpp 链接 libunity.so → adb push + run-as 推送到手机 → 启动游戏抓取 [Leap] 构建时间戳日志验证 so 已更新 → 还原 Player.cpp。触发：编译推送、推so、换so到手机、leap-android-build-push、验证手机so是否更新。用户未指定国服/西方包时必须先询问选择哪个包。
---

# Android Build & Push

CODM 引擎（G:\UnitySourceCODM）Android so 的完整工作流：**门禁 → 注入 → 编译 → 链接 → 推送 → 启动验证 → 还原**。全程基于设备日志中的 `[Leap]` 构建时间戳判断 so 是否更新。

## 0. 关键路径与配置（已验证事实）

| 项 | 路径/值 |
|---|---|
| 引擎源码 | `G:\UnitySourceCODM` |
| 工作区 | `G:\CODM_CHN` |
| il2cpp 产物（generatedcppdir） | `G:\CODM_CHN\il2cppOutput_codm-Android` |
| il2cpp 缓存 | `G:\CODM_CHN\il2cpp_cache\il2cpp_cache-Android` |
| NDK r27d | `G:\CODM_CHN\CI\lib\win\android\ndk\android-ndk-r27d` |
| il2cpp 编译器 | `G:\CODM_CHN\CI\bin\il2cpp-compile\il2cpp.dll`（dotnet 运行） |
| so 输出 | `G:\CODM_CHN\symbols\libunity.so`（+ `.debug` / `.sym`） |
| 构建脚本参考 | `G:\CODM_CHN\CI\test\il2cpp-compile-android.bat`（模板，勿直接执行） |
| MobileDevTool 生成的可执行脚本 | `C:\Users\<user>\MobileDevToolData\build-scripts\il2cpp-compile-android-Debug.bat` |
| 国服包名 | `com.tencent.tmgp.cod` |
| 西方包名 | `com.activision.callofduty.shooter` |
| [Leap] 日志注入锚点 | `Runtime\Misc\Player.cpp` 的 `PlayerInitEngineGraphics()` 内 **`[PCHD]` 日志行之后**（见 §2.2） |
| 用户配置 | `%USERPROFILE%\cpToolConfig\toolsetting.json`（workspace/engine_dir/default_so_path/hotfix_so_branch/configurations 等） |
| 热修 so 专用分支 | `local/cptools-so-hotfix`（来自 toolsetting.json 的 `hotfix_so_branch`） |

默认构建配置：**debug + developmentPlayer=1 + arm64 + QTS**（与 MobileDevTool 的 `configurations.Android_64_Debug` 一致）。

> MobileDevTool 的职责边界：它只按 `toolsetting.json` 的 `configurations.<name>` 模板渲染出两个 bat（Bee + il2cpp 链接）并执行，**不做 [Leap] 注入、不做分支/版本门禁**。注入与门禁是本 skill 独有的前置层。

## 1. 分支 / 工作区 / 包版本门禁（编译前必须通过）

**目的**：防止把错误分支或未提交改动编进 so、防止跨基线把 so 推到不匹配的手机包上（可能导致崩溃或验收失真）。任一检查不通过即停下询问用户，不盲目续跑。

### 1.1 分支检查

```powershell
Set-Location G:\UnitySourceCODM
$expected = (Get-Content "$env:USERPROFILE\cpToolConfig\toolsetting.json" | ConvertFrom-Json).hotfix_so_branch  # local/cptools-so-hotfix
$current  = git branch --show-current
if ($current -ne $expected) {
    Write-Warning "当前分支 '$current' != 热修分支 '$expected'"
    # 不强制切换——询问用户：是切到热修分支，还是确认就在当前分支构建
}
```

- 默认期望在 `hotfix_so_branch`（`local/cptools-so-hotfix`）上构建。若用户明确要在当前工作分支上验证改动，记录分支名后继续，但报告里必须标注「非标准热修分支构建」。

### 1.2 工作区干净度检查

```powershell
$dirty = git status --porcelain
if ($dirty) {
    Write-Warning "工作区有未提交改动，会被编进 so："
    git status --short
    # 列出后由用户确认：这些改动是否就是本次要验证的内容
}
```

- 未提交改动会被编进 so。若是用户本次想验证的改动则继续；若是无关残留，提示先 stash/commit。

### 1.3 包版本核对（防跨基线推 so）

```powershell
# 手机端实际包版本
$pkg = 'com.tencent.tmgp.cod'   # 或 com.activision.callofduty.shooter
$verLine = adb shell dumpsys package $pkg | Select-String 'versionCode|versionName'
# 例：versionCode=17828 versionName=1.0.57

# 本地对应构建指纹（MobileDevTool 下载 artifacts 的目录名含基线标签）
$code = ([regex]::Match(($verLine | Select-String 'versionCode'), '\d+')).Value
Get-ChildItem "$env:USERPROFILE\MobileDevToolData\artifacts" -Directory |
    Where-Object Name -like "*$code*" | Select-Object -ExpandProperty Name
# 例：codm-Android-TRUNK-iMSDK_King-none-L-1.0.57.17828-090212-R1983614-<git-sha>.apks
```

- 从 artifacts 目录名可读出该包的 **分支基线标签**（`TRUNK` / `WWL39.1_33.1` 等）与 **git-sha**。若与当前引擎分支基线明显不符（如包是 TRUNK 主干，本地却在旧发布分支），提示用户确认 so 与该包兼容后再继续。
- 参考实测：国服 `1.9.57`(4595)、西方 `1.0.57`(17828)，`last_modify_version=1.0.57.17828`、`last_install_package=com.activision.callofduty.shooter`。

## 2. [Leap] 时间戳自动注入（编译前必须，否则验收点失效）

### 2.1 为什么必须每次注入

`[Leap]` 打印的 `__DATE__`/`__TIME__` 是 **Player.cpp 的编译期常量**。Bee 按**文件内容哈希**判断是否重编，只改 mtime（touch）无效。如果本次 Player.cpp 没变化，它就不重编，`[Leap]` 会停在旧时间——**即使 so 已更新，验收点也读不出**。所以每次构建前都要让 Player.cpp 内容真实变化一次。

### 2.2 模板注入（幂等）

当前源码里**没有** `[Leap]` 代码（已实测确认），锚点改为稳定存在的 `[PCHD]` 日志行。注入逻辑分三种情况：

- **已有 LEAP-INJECT 标记块** → 只更新块内时间戳（改内容触发重编）
- **无标记块** → 在 `[PCHD]` 行之后注入整块模板
- **找不到 `[PCHD]` 锚点** → throw，提示注入点已移动，人工确认

```powershell
$pc = 'G:\UnitySourceCODM\Runtime\Misc\Player.cpp'
$orig = [System.IO.File]::ReadAllText($pc)
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# 注入模板（C# 源码块，解析 __DATE__/__TIME__ 并打 [Leap] 日志）
$block = @"
        // LEAP-INJECT-BEGIN (build stamp: $stamp)
        {
            const char* d = __DATE__;  // "Mmm dd yyyy"（日可能空格补位）
            const char* t = __TIME__;  // "hh:mm:ss"
            int month = 0, day = 0, hour = 0, minute = 0;
            {   // 简化解包：Mmm
                const char* m = d; char m3[4] = {m[0],m[1],m[2],0};
                const char* names = "JanFebMarAprMayJunJulAugSepOctNovDec";
                for (int i=0;i<12;i++) if (strncmp(m3, names+i*3, 3)==0) { month=i+1; break; }
            }
            day   = (d[4]==' ' ? 0 : d[4]-'0')*10 + (d[5]-'0');
            hour  = (t[0]-'0')*10 + (t[1]-'0');
            minute= (t[3]-'0')*10 + (t[4]-'0');
            LogStringMsg("[Leap] %02d%02d,%02d:%02d (libunity build %s %s)", month, day, hour, minute, __DATE__, __TIME__);
        }
        // LEAP-INJECT-END
"@

$anchor = '        LogStringMsg("[PCHD] IsPCHD()=%d (platform branch: %s)", (int)IsPCHD(), IsPCHD() ? "PC High Definition" : "Mobile");'

if ($orig -match 'LEAP-INJECT-BEGIN \(build stamp: .*\)') {
    # 幂等：已注入 → 只更新时间戳
    $new = $orig -replace 'LEAP-INJECT-BEGIN \(build stamp: .*\)', "LEAP-INJECT-BEGIN (build stamp: $stamp)"
    [System.IO.File]::WriteAllText($pc, $new)
    Write-Host "[Leap] 标记时间戳已更新: $stamp"
} elseif ($orig -match [regex]::Escape($anchor)) {
    # 首次注入：在 [PCHD] 行后插入整块
    $new = $orig -replace [regex]::Escape($anchor), ($anchor + "`r`n" + $block)
    [System.IO.File]::WriteAllText($pc, $new)
    Write-Host "[Leap] 模板已注入（锚点 [PCHD]）: $stamp"
} else {
    throw "Player.cpp 中未找到 [PCHD] 锚点，注入点可能已移动，请人工确认 PlayerInitEngineGraphics()"
}
```

> 说明：注入块内即包含完整 `[Leap]` 日志代码，不依赖源码里预先存在 `[Leap]`。块用 `LEAP-INJECT-BEGIN/END` 包裹，便于 §6 精确删除还原。

## 3. Bee 编译 AndroidPlayer（增量）

```powershell
Set-Location G:\UnitySourceCODM
$env:VSLANG='1033'
perl bee.pl AndroidPlayer --platform=android --config=debug --scriptingBackend=il2cpp --useQTS=1 --developmentPlayer=1 --arch=arm64
```

- 后台运行（job_output 等待），成功标志 `Tundra build success`。
- 无源码变更时 0 items updated（静态库已是最新，直接跳到链接）。
- 产物：`build\AndroidPlayer\Variations\il2cpp\Debug\StaticLibs\arm64-v8a\libunityruntime.a`
- 注意：**不要**用 `cmd /c "... set X=%VAR%&& ..."` 单行内联——`%VAR%` 在 cmd 解析期展开，会传字面量给 bee.pl 导致 DAG profile 混乱。参数直接写死。
- MobileDevTool 对应脚本：`build-scripts\BuildAndroidSupport.Bee.Debug.bat`（内容与上面一致，已 `--verbose`）。

## 4. il2cpp 链接 libunity.so

在 **pwsh**（不是 cmd）中设置环境变量后运行。**这些环境变量缺一不可**（漏了会报 `ArgumentNullException: UNITY_ANDROIDPLAYER_RUNTIME_CONFIGURATION` / `DirectoryNotFoundException: UNITY_ANDROIDPLAYER_DIR`）：

```powershell
$env:WORKSPACE_PARENT='G:\CODM_CHN'
$env:IL2CPP_OUTPUT='G:\CODM_CHN\il2cppOutput_codm-Android'
$env:ANDROID_NDK_ROOT='G:\CODM_CHN\CI\lib\win\android\ndk\android-ndk-r27d'
$env:IL2CPP_ROOT_DIR_PATH='G:\CODM_CHN\CI\il2cpp'
$env:IL2CPP_ENABLE_COMPILE_CACHE='1'
$env:UNITY_ANDROIDPLAYER_RUNTIME_CONFIGURATION='Debug'
$env:UNITY_ANDROIDPLAYER_DIR='G:/UnitySourceCODM/build/AndroidPlayer'

dotnet G:\CODM_CHN\CI\bin\il2cpp-compile\il2cpp.dll --compile-cpp --libil2cpp-static `
  --platform=Android --architecture=ARM64 --configuration=Debug `
  --outputpath="G:/CODM_CHN/symbols/libunity.so" `
  --cachedirectory="G:\CODM_CHN\il2cpp_cache\il2cpp_cache-Android" `
  --tool-chain-path="$env:ANDROID_NDK_ROOT" `
  --generatedcppdir="$env:IL2CPP_OUTPUT" --linker=lld
```

- 后台运行，全量链接约 20-40 秒（缓存命中时更快）。
- 成功标志：`Total link time: N milliseconds` 且无 Exception；产物时间戳更新，`.so`（strip 后约 880 MB）、`.debug`、`.sym` 三件套齐。
- 链接输出巨大（含完整 link 响应文件），务必重定向到日志文件再 grep，不要直接管道读。

### 备选：直接用 MobileDevTool 生成的脚本

```powershell
cmd /c "C:\Users\<user>\MobileDevToolData\build-scripts\il2cpp-compile-android-Debug.bat"
```

（该 bat 已内置全部环境变量；只有当它不存在时才走上面的手动环境变量方式。）

## 5. 推送到手机

推送前检查：`adb shell pm path <pkg>` 确认已安装；`adb shell run-as <pkg> ls files/` 确认是 debuggable 包（run-as 成功）。非 debuggable 包 run-as 会失败，此时应告知用户需要重签名包（ApkRepackage 流程），不要硬推。

```powershell
adb push G:\CODM_CHN\symbols\libunity.so /data/local/tmp/libunity.so
adb shell "run-as <包名> cp /data/local/tmp/libunity.so files/libunity.so && run-as <包名> chmod 755 files/libunity.so && rm /data/local/tmp/libunity.so && run-as <包名> ls -l files/libunity.so"
```

- push 约 9 秒（~94 MB/s）。
- 验证：`ls -l` 输出的字节数必须等于本地 `libunity.so` 的 Length。
- so 放在应用 `files/` 目录（运行时从 `/data/user/0/<pkg>/files/` 加载，覆盖 apk 内的版本）。

## 6. 启动 + [Leap] 日志验证 + 还原 Player.cpp

### 6.1 抓日志验证

```powershell
adb logcat -c
adb shell am force-stop <包名>
Start-Sleep -Seconds 2
adb shell monkey -p <包名> -c android.intent.category.LAUNCHER 1
Start-Sleep -Seconds 20   # 引擎初始化需要时间
adb logcat -d | Select-String '\[Leap\]|\[PCHD\]'
```

期望输出：

```
[PCHD] IsPCHD()=0 (platform branch: Mobile)
[Leap] 0906,15:14 (libunity build Sep  6 2026 15:14:50)
```

判定规则：
- `[Leap]` 的 MMDD,HH:MM = **本次 Bee 编译 Player.cpp 的时间**（略早于链接完成时间，属正常——`__TIME__` 是编译期常量）。与本次构建时间吻合 → so 已更新 ✅
- 显示旧时间或无该行 → 手机跑的还是旧 so ❌（排查：是否推错包、run-as 是否成功、游戏是否真重启）
- 因为第 2 步已强制重编 Player.cpp，正常构建的 `[Leap]` **必定等于本次构建时间**；若仍是旧时间，说明注入没生效（检查是否报「未找到锚点」）。

### 6.2 验证后还原 Player.cpp（必须，避免污染 git）

按 `LEAP-INJECT-BEGIN/END` 标记整块删除（不依赖临时备份文件，也不会误删别人的新改动）：

```powershell
$pc = 'G:\UnitySourceCODM\Runtime\Misc\Player.cpp'
$cur = [System.IO.File]::ReadAllText($pc)
if ($cur -match '(?s)\r?\n?        // LEAP-INJECT-BEGIN .*?        // LEAP-INJECT-END\r?\n?') {
    $new = [regex]::Replace($cur, '(?s)\r?\n?        // LEAP-INJECT-BEGIN .*?        // LEAP-INJECT-END\r?\n?', "`r`n")
    [System.IO.File]::WriteAllText($pc, $new)
    Write-Host "Player.cpp 已还原（LEAP-INJECT 块已移除）"
    Set-Location G:\UnitySourceCODM; git diff --stat Runtime/Misc/Player.cpp  # 应输出空 = 内容已还原
}
```

> 已编译进 so 的 `__DATE__`/`__TIME__` 不受还原影响——so 里保留的就是本次构建时间。还原只为了让 git 工作区不留无关 diff。**下次构建会重新走第 2 步注入。**

## 7. [Leap] 日志的维护

时间戳代码由第 2 步在构建前注入到 `Runtime\Misc\Player.cpp` 的 `PlayerInitEngineGraphics()` 内（`[PCHD]` 日志之后），推送验证后按标记删除。它解析 `__DATE__`（"Mmm dd yyyy"，日可能空格补位）/`__TIME__`（"hh:mm:ss"）输出 `MMDD,HH:MM`。

**关键机制**：`__DATE__`/`__TIME__` 是编译期常量，只在 Player.cpp **被重新编译**时刷新。Bee 按内容哈希判断重编，所以本 skill 用「每次构建前注入/更新时间戳」来强制刷新。若换注入点，保持放在引擎初始化早期（logcat 可见的 Unity tag），并同步更新第 2 步的 `$anchor` 锚点字符串。

## 8. 排错速查

| 症状 | 原因/处理 |
|---|---|
| bee.pl 报 FastCopyDirectory duplicate target | 上次以错误参数触发了 DAG 重生成；直接用完整正确参数重跑 |
| il2cpp ArgumentNullException: UNITY_ANDROIDPLAYER_RUNTIME_CONFIGURATION | 漏设该环境变量（见第 4 步清单） |
| il2cpp DirectoryNotFoundException: UNITY_ANDROIDPLAYER_DIR | 漏设该环境变量 |
| il2cpp Android NDK path does not exist: %ANDROID_NDK_ROOT% | 用了 cmd /c 内联 %VAR%，改在 pwsh 里设置或内联实际路径 |
| run-as 失败 | 包不是 debuggable；需 ApkRepackage 重签名流程（G:\CODM_CHN\Client_Tools\CGame_Debugger\ApkRepackage） |
| [Leap] 时间没变 | 几乎一定是第 2 步注入没执行或没生效（Player.cpp 没重编）。确认构建前跑了注入且没报「未找到锚点」；Bee 输出里应能看到 `Runtime_Misc_*.o`（含 Player.cpp 的目标）被重编。touch mtime 无效，必须改内容 |
| 注入报「未找到 [PCHD] 锚点」 | PlayerInitEngineGraphics() 结构变了，人工确认 [PCHD] 日志行位置后更新 `$anchor` |
| 推送后游戏崩溃 | 检查 so 架构（arm64）与配置（Debug so 配 Debug 包）；检查第 1.3 步包版本基线是否匹配；符号不一致用 `G:\CODM_CHN\symbols\libunity.so.debug` 挂 LLDB |

## 9. 执行纪律

- **编译前依次过 §1 三道门禁**（分支 / 工作区 / 包版本），任一不通过即停下询问用户，不盲目续跑。
- **门禁通过后必须执行第 2 步注入**（真实改动 Player.cpp 内容），否则验收点失效；推送验证后按第 6.2 步还原。
- 长命令（Bee、链接、push）用 run_in_background + job_output 等待；不要前台裸跑阻塞。
- 每步完成后立即校验产物（时间戳/字节数），失败即停，不盲目续跑。
- 推送前 `adb devices` 确认设备在线；多设备时用 `-s <serial>`。
- 报告以「本地产物时间戳 vs 设备 [Leap] 时间戳」收尾，这是本 skill 的核心验收点。
