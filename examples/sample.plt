defconst [one : Int]  1

let [y : Nat] be 5 in:
    y + 3

defunc foo : [y : Int] -> Int:
    y - one

defunc bar1 : [y : Int] -> [x : Nat] -> Int:
    x + y

let [bar : [a : Nat] -> [b : Nat] -> Nat] be lambda [x : Nat] : lambda [y : Nat] : x + y in:
    let [foo : [y : Int] -> Int] be lambda [d : Nat] : d in:
        
   
bar(1 foo(one))

foo(one)

bar1(1 foo(one))
