let [x : Nat] be 5 in:
    x + 1

let [x : Int] be 5 in:
    let [z : Nat] be 10 in:
        let [f : [x : Int] -> Nat] be 
                (lambda [x : Int] : z) in:
            f(x) + z

let [f : [g : (Nat -> Nat)] -> Nat -> Nat] 
    be lambda [g : Nat -> Nat] : lambda [x : Nat] : g(x)
    in: let [op : Nat -> Nat] be lambda [x : Nat] : 1 + x
        in: f(op 4) 

let [ls : List Int] be [1,2,-3,4] in:
    let [map : (Int -> Int) -> ((List Int) -> (List Int))] 
        be
            lambda [f : (Int -> Int)] : 
                lambda [ls : List Int] :
                    let [out_ty : [l : List Int] -> (Universe 0)] 
                        be lambda [l : List Int] : (List Int) 
                        in: induct 
                                ls 
                                out_ty 
                                []
                                lambda [x : Int] : 
                                    lambda [ans : List Int] : [
                                        f(x)] + ans
                                qed
        in:
            let [op : [z : Int] -> Int] 
                be (lambda [z : Int] : 1 + z)
                in:
                    map(op ls)

            


