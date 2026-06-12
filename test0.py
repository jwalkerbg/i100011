from typing import Any

def func(ss:str, ii:int, ff:float,**options:Any):
    print(f"ss: {ss}, ii: {ii}, ff: {ff}")
    print(f"options: {options}")


if __name__ == "__main__":
    print(f"\n")
    func(ss="string", ii=98, ff="10.98",op="56",bubi=544)
