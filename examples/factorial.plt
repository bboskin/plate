defunc fact : [i : Nat] -> Nat:
    if i == 0 then 1
    else let [x : Nat] be fact(i - 1) in:
        1 + x
