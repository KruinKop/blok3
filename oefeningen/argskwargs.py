def my_sum(*args):
    som = 0
    for arg in args:
        som += arg
    return som

print(my_sum(1,2,3,4,5))

def make_uppercase_dict(**kwargs):
    uppercase_dict = {}
    for key, value in kwargs.items():
        uppercase_dict[key] = value.upper()
    return uppercase_dict

print(make_uppercase_dict(maandag = "spaghetti", dinsdag = "ramen", woensdag = "patat"))