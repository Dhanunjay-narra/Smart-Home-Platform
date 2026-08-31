import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def fix_tests():
    test_dir = ROOT / "tests"
    for current, _, files in os.walk(test_dir):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                p = Path(current) / f
                with open(p, "r", encoding="utf-8") as fp:
                    content = fp.read()
                
                # Replace @pytest.mark.asyncio def test_xxx(...): with def test_xxx(...): asyncio.run(_inner())
                lines = content.splitlines()
                new_lines = []
                in_async_test = False
                async_func_name = ""
                
                for line in lines:
                    if line.strip() == "@pytest.mark.asyncio":
                        continue
                    if line.strip().startswith("async def test_"):
                        # Convert to def test_...: asyncio.run(async def _async_impl(): ...)
                        func_match = re.match(r"\s*async\s+def\s+(test_\w+)\s*\((.*?)\)\s*:", line)
                        if func_match:
                            func_name = func_match.group(1)
                            new_lines.append(f"def {func_name}():")
                            new_lines.append(f"    async def _async_impl():")
                            in_async_test = True
                            continue
                    
                    if in_async_test:
                        if line.startswith("def ") or (line.strip().startswith("def ") and not line.startswith("    ")):
                            # End of previous async function
                            new_lines.append("    import asyncio")
                            new_lines.append("    asyncio.run(_async_impl())")
                            new_lines.append("")
                            in_async_test = False
                        else:
                            new_lines.append("    " + line)
                            continue

                    new_lines.append(line)

                if in_async_test:
                    new_lines.append("    import asyncio")
                    new_lines.append("    asyncio.run(_async_impl())")

                with open(p, "w", encoding="utf-8") as fp:
                    fp.write("\n".join(new_lines) + "\n")
    print("Test runners fixed to use asyncio.run().")

if __name__ == "__main__":
    fix_tests()
