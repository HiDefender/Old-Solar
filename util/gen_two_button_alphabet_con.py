
off_buttons = []
on_buttons = []
for i in range(12):
    off_buttons.append(f"Extract({i}, {i}, b.G[i]) == 0, ")
    on_buttons.append(f"Extract({i}, {i}, b.G[i]) == 1, ")

con_parts = []
for missing in range(12):
    part = "\tAnd("
    for con in range(12):
        if con != missing:
            part += off_buttons[con]
        else:
            part += on_buttons[con]
    part = part[:-2] + "),\n"
    con_parts.append(part)


for missing_1 in range(11):
    for missing_2 in range(missing_1 + 1, 12):
        part = "\tAnd("
        for con in range(12):
            if con != missing_1 and con != missing_2:
                part += off_buttons[con]
            else:
                part += on_buttons[con]
        part = part[:-2] + "),\n"
        con_parts.append(part)

final_con = "Or("
for i in range(len(con_parts)):
    final_con += con_parts[i]

final_con = final_con[:-2] + "\n)"
print(final_con)