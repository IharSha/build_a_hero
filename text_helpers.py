def out_label():
    return "\n--> "


def input_line(text: str = "") -> str:
    ans = input(f"{text}{out_label()}")
    if ans in ("q", "Q"):
        raise SystemExit

    return ans


def print_input_options(options: dict) -> None:
    print("\nSelect option:")
    counter = 0
    for opt in options.values():
        if counter > 3:
            counter = 0
            print("\n")
        print(f"{opt[0]}. {opt[1]}", end="\t"*4)
        counter += 1
