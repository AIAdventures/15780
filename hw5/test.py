import problems

q = [[0.0,0.0], [0.0,0.0], [0.0,0.0], [0.0,0.0]]
problems.ql_update(q,0.3,0.9,2,1,2.62075930591,0)
#Updated q: [[0.0, 0.0], [0.0, 0.0], [0.0, 0.7862277917740591], [0.0, 0.0]]
print q
print problems.ql_policy(q)
problems.ql_update(q,0.3,0.9,2,1,2.62075930591, 1)
#Updated q: [[0.0, 0.0], [0.0, 0.0], [0.0, 1.3365872460159003], [0.0, 0.0]]
print q
print problems.ql_policy(q)

problems.ql_update(q,0.3,0.9,3,1,0.560372440384,2)
#Updated q: [[0.0, 0.0], [0.0, 0.0], [0.0, 1.3365872460159003], [0.0,
#0.5289902885396414]]
print q
print problems.ql_policy(q)

problems.ql_update(q,0.3,0.9,2,0,0.300354515827,0)
#Updated q: [[0.0, 0.0], [0.0, 0.0], [0.0901063547480966, 1.3365872460159003],
#[0.0, 0.5289902885396414]]
print q
print problems.ql_policy(q)

problems.ql_update(q,0.3,0.9,2,0,0.300354515827,1)
#Updated q: [[0.0, 0.0], [0.0, 0.0], [0.1531808030717642, 1.3365872460159003],
#[0.0, 0.5289902885396414]]
print q
print problems.ql_policy(q)
