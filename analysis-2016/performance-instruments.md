# Performance, Profiling & Battery — WWDC 2016 Analysis

**Sessions covered:** 406 (Optimizing App Startup Time), 411 (System Trace in Depth), 412 (Thread Sanitizer and Static Analysis), 416 (Understanding Swift Performance), 417 (Debugging Tips and Tricks), 418 (Using Time Profiler in Instruments), 419 (Protocol and Value Oriented Programming in UIKit Apps), 421 (System Trace), 720 (Concurrent Programming With GCD in Swift 3), 721 (Unified Logging and Activity Tracing), 719 (Optimizing I/O for Performance and Battery Life)

## Headline

Three big themes:
1. **Launch performance** — `dyld` gets new diagnostics; the 400ms first-frame target is reaffirmed; recommended techniques (fewer dylibs, fewer Obj-C classes, no static initializers).
2. **Thread Sanitizer** ships in Xcode 8 — runtime data-race detection. Pair with the existing AddressSanitizer.
3. **Unified Logging (`os_log`)** replaces NSLog and Apple System Logger. `os_signpost` for activity tracing.

## Launch time — the 400ms target (session 406)

- **400ms** is the goal — covers the launch animation cleanly. Above that, users perceive lag.
- **20s** is the hard cap before iOS kills your app for a watchdog timeout.
- **Measure on your slowest supported device** — these are constant timeouts, not relative.
- **Cold launch** (post-reboot, app not in disk cache) is the important case. Reboot between measurements. Warm launches improve as cold launches do.

### What happens before main()

```
exec → kernel maps main binary + dyld at random address
dyld:
  1. Load all dependent dylibs (recursive)
  2. Rebase fix-ups (data pointers internal to each dylib, adjusted for ASLR)
  3. Bind fix-ups (data pointers across dylibs, by symbol name)
  4. ObjC setup (class registration, ivar offsets, category fix-ups, selector uniquing)
  5. Initializers (+load, C++ constructors, attribute((constructor)))
  6. Call main()
```

### Measure with `DYLD_PRINT_STATISTICS` (NEW improved output)

Set the environment variable in your scheme. Xcode 8 produces an actionable breakdown:

```
Total pre-main time: 350ms
  dylib loading time: 100ms (26 dylibs)
  rebase/binding time: 150ms (12,000 fixups)
  ObjC setup time: 30ms
  initializer time: 70ms
```

The debugger pause-on-dylib-load adds significant time over USB; `dyld` subtracts it from the reported numbers. Wall-clock observed time will be larger.

### Reduction strategies

**1. Fewer dylibs.** Average app loads 100–400. OS dylibs are pre-cached and fast; **embedded** dylibs are not. Each embedded dylib pays mmap, validation, code-sign registration, fix-ups. Apple's recommendation: **target ~6 embedded dylibs.** Merge libraries; use static archives where possible. Use `dlopen` only as a last resort.

**2. Fewer ObjC classes / less ObjC metadata.** Each class adds entries to data pointer tables that need fix-up. 10k classes can add ~700ms. Use Swift structs (don't generate ObjC metadata). Avoid C++ V-tables (also create rebaseable pointer tables).

**3. Remove explicit initializers.**
- Replace `+load` (deprecated for this reason) with `+initialize` — runs lazily on first class use, not at load time.
- Replace `__attribute__((constructor))` and C++ globals with non-trivial constructors with **call-site initializers**: `dispatch_once`, `pthread_once`, `std::call_once`.
- Make C++ globals POD (plain old data) — the linker pre-computes them.
- **Move to Swift** — Swift global variable initialization automatically uses `dispatch_once` under the hood.
- **Never `dlopen` from an initializer** — turns off dyld's locking optimization (single-threaded assumption).
- **Never start threads from an initializer** — same reason.
- Compiler flag `-Wglobal-constructors` warns whenever you generate one.

**4. Lazy-init expensive class state via `dispatch_once` patterns.**

### Use the new "DYLD_PRINT_STATISTICS_DETAILS" (Xcode 8)

Per-image breakdown of which dylib took the most time. Pinpoints the offender.

## Thread Sanitizer (NEW in Xcode 8)

Compile with `-fsanitize=thread`. Runtime instrumentation detects:

- **Data races** — concurrent unsynchronized access to the same memory location.
- **Use-after-free** in concurrent contexts.
- **Lock-order violations** that could deadlock.

Performance overhead is significant — TSAN is a CI/test/development tool, not for production builds. Pair with AddressSanitizer (cannot run both simultaneously).

```swift
class Counter {
    var value = 0       // RACE: concurrent write from multiple queues
    func increment() { value += 1 }
}
```

TSAN reports the race with stack traces of each conflicting access and the involved threads. Hard to detect by hand; trivial to find with TSAN.

**BEST PRACTICE:** Run TSAN as part of CI. It catches latent bugs that survive years undetected because they only manifest under contention.

## Unified Logging (`os_log`)

Replaces `NSLog`, replaces ASL (`asl_log`), replaces print-to-stderr habits.

```swift
import os.log

let log = OSLog(subsystem: "com.example.foo", category: "networking")

os_log("Request started", log: log, type: .info)
os_log("Got response %d in %{public}s", log: log, type: .debug, statusCode, requestURL)
os_log("FAILED: %{public}@", log: log, type: .error, error.localizedDescription)
```

Key features:
- **Highly performant** — log calls are essentially free until the system decides to materialize the message (decoded only when read).
- **Privacy-aware format specifiers** — `%{private}s` (default for strings/objects/data) redacts on persistence; `%{public}s` opts in to including the value.
- **Categorization** by subsystem + category — filter in Console.app or `log stream` CLI.
- **5 levels** — `.default`, `.info`, `.debug`, `.error`, `.fault`.
- **Activity tracing** with `os_signpost` (introduced 2017, but `OSActivity` is in 2016).

`log stream --predicate 'subsystem == "com.example.foo"'` from Terminal — live tail with predicate filtering.

**HIDDEN GEM:** Logged strings are stored in compressed format with format string + arguments separately. Persistence is privacy-aware. Decoded only when needed. Unlike NSLog, ten million `os_log` calls/sec barely register.

## Time Profiler & System Trace (sessions 411, 418, 421)

Time Profiler now supports:
- Filter by thread / queue.
- Show Obj-C/Swift demangled symbols by default.
- "Heaviest Stack Trace" view shows the dominant call path.
- Symbolicates running on simulator AND device.

System Trace combines CPU usage, scheduling, virtual memory, system calls, syscalls, and thread state changes (running/runnable/blocked) into one timeline. Use to diagnose:
- Thread starvation (running but not making progress).
- Excessive page faults (virtual memory column shows the pattern).
- Lock contention (ThreadState shows blocked-on-mutex periods).

## I/O performance and battery (session 719)

- **Coalesce writes** — flash writes are far more expensive than reads. 4KB writes amortize poorly; use larger blocks.
- **`posix_fadvise()` / `madvise()`** — tell the kernel about your access pattern (sequential, random, willneed, dontneed).
- **`fsync` is expensive** — it drains journal + disk cache. Use atomic Foundation APIs (`Data.write(to:options:[.atomic])`) instead of repeatedly fsync-ing manual writes.
- **Don't poll files** — use `DispatchSourceFileSystemObject` for kernel-driven change notification.
- **Memory-map (`mmap`) read-mostly files** — leverages the page cache as your free LRU.
- **Background activities should respect `NSProcessInfo.beginActivity(options:reason:)`** — system can defer your work during user-active periods.

## Swift performance recap (session 416, paired with this analysis)

See `swift-3-migration.md` for the full breakdown. Quick rules:
- **Structs over classes** by default. Stack-allocated, no reference counting, static dispatch.
- **`final class`** for non-subclassed reference types — devirtualizes calls.
- **Whole-Module Optimization on by default** in Xcode 8. Existing projects get a one-shot suggestion.
- **Protocol-typed properties with large structs** cost a heap alloc. Use copy-on-write via `isUniquelyReferenced(_:)`.
- **Generics specialize** when caller and callee are in the same module (or with WMO across files).

## Best practices summary

- Set `DYLD_PRINT_STATISTICS = 1` in your test scheme. Track it over time.
- Cap embedded dylibs at ~6.
- Replace `+load` with `+initialize`; remove C++ globals with non-trivial constructors.
- Use `dispatch_once` for all one-shot initialization.
- Run TSAN in CI for any concurrent code.
- Migrate logging from `NSLog`/`print` to `os_log` with subsystem + category.
- Use `os_log %{public}` opt-in for non-PII strings; let the default redact PII.
- Use `posix_fadvise(SEQUENTIAL)` when reading large files top-to-bottom.
- Profile cold launches on slowest supported device.

## Hidden gems summary

- `DYLD_PRINT_STATISTICS_DETAILS` (Xcode 8) shows per-image timings.
- `os_log` is essentially free until decoded.
- TSAN finds data races static analysis can't.
- `+initialize` is lazy — no launch-time hit unless used.
- `posix_fadvise(POSIX_FADV_SEQUENTIAL)` triggers kernel readahead.
- `dispatchPrecondition(condition: .onQueue(q))` enforces thread-invariant runtime checks.

## Cross-references

- Swift performance internals → analysis-2016/swift-3-migration.md
- watchOS 3 background CPU caps → analysis-2016/watchos3-redesign.md
- GCD modernization → analysis-2016/swift-3-migration.md
