defunc fact : [i : Nat] -> Nat:
    let [j : Rational] = i in:
        if i == 0 then 1
        else let [x : Nat] be fact(i - 1) in:
            1 + x
