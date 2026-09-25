import re

with open('src/py_plaque_inc/map/geo_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'Erstellt die Weltkarte mit 49 detaillierten Territorien,',
    'Erstellt die Weltkarte mit 51 detaillierten Territorien,'
)

old_deu = """        Country(
            id="deu",
            name="Deutschland",
            population=102_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(642, 300),
            polygons=[
                [(636, 277), (648, 279), (650, 282), (654, 297), (648, 300), (651, 306), (647, 310), (655, 318), (652, 321), (643, 317), (639, 312), (633, 311), (629, 305), (632, 298), (621, 291), (635, 278)],
            ],
            neighbors=["bal", "fra", "ita", "pol", "sca"],
        ),"""

new_deu = """        Country(
            id="deu",
            name="Deutschland",
            population=84_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(640, 291),
            polygons=[
                [(635, 277), (647, 278), (650, 282), (652, 292), (649, 304), (634, 305), (631, 302), (628, 296), (626, 287), (635, 277)],
            ],
            neighbors=["ceu", "fra", "pol", "sca"],
        ),
        Country(
            id="ceu",
            name="Zentraleuropa",
            population=68_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=False,
            capital_pos=(648, 312),
            polygons=[
                [(634, 305), (649, 304), (664, 305), (669, 310), (668, 316), (658, 318), (650, 321), (638, 320), (631, 317), (628, 310), (634, 305)],
            ],
            neighbors=["bal", "deu", "fra", "ita", "pol", "ukr"],
        ),"""
assert old_deu in code, "old_deu not found"
code = code.replace(old_deu, new_deu)

old_fra = """        Country(
            id="fra",
            name="Frankreich",
            population=80_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(612, 308),
            polygons=[
                [(624, 284), (626, 286), (621, 292), (630, 297), (631, 301), (628, 304), (633, 312), (630, 315), (622, 314), (614, 323), (615, 325), (623, 324), (614, 327), (612, 323), (608, 331), (590, 316), (582, 316), (588, 312), (604, 313), (606, 307), (602, 302), (596, 300), (597, 298), (614, 293)],
            ],
            neighbors=["deu", "esp", "gbr", "ita"],
        ),"""

new_fra = """        Country(
            id="fra",
            name="Frankreich",
            population=80_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(610, 306),
            polygons=[
                [(623, 285), (626, 287), (628, 296), (631, 302), (634, 305), (628, 310), (631, 317), (634, 322), (624, 324), (614, 326), (612, 323), (606, 326), (589, 320), (582, 316), (588, 312), (603, 312), (606, 306), (600, 300), (596, 298), (614, 293), (623, 285)],
            ],
            neighbors=["ceu", "deu", "esp", "gbr", "ita"],
        ),"""
assert old_fra in code, "old_fra not found"
code = code.replace(old_fra, new_fra)

old_esp = """        Country(
            id="esp",
            name="Spanien",
            population=58_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(589, 329),
            polygons=[
                [(583, 316), (600, 323), (606, 329), (605, 333), (597, 333), (599, 342), (585, 345), (584, 342), (591, 337), (590, 333), (582, 331), (582, 324), (569, 322), (581, 322), (583, 317)],
            ],
            neighbors=["fra", "nab"],
        ),"""

new_esp = """        Country(
            id="esp",
            name="Spanien",
            population=58_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(588, 330),
            polygons=[
                [(582, 316), (589, 320), (606, 326), (604, 332), (597, 333), (599, 342), (585, 345), (583, 341), (578, 338), (574, 331), (576, 323), (582, 316)],
            ],
            neighbors=["fra", "nab"],
        ),"""
assert old_esp in code, "old_esp not found"
code = code.replace(old_esp, new_esp)

old_ita = """        Country(
            id="ita",
            name="Italien",
            population=59_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(657, 324),
            polygons=[
                [(656, 317), (666, 324), (662, 324), (660, 330), (654, 333), (647, 329), (657, 329), (658, 325), (654, 322)],
                [(639, 331), (644, 333), (640, 346), (635, 342), (636, 332), (638, 332)],
            ],
            neighbors=["bal", "deu", "fra"],
        ),"""

new_ita = """        Country(
            id="ita",
            name="Italien",
            population=59_000_000,
            climate=Climate.HOT,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(649, 331),
            polygons=[
                [(631, 317), (638, 320), (650, 321), (658, 318), (664, 323), (660, 330), (654, 334), (649, 336), (652, 338), (648, 342), (644, 338), (644, 333), (639, 327), (634, 322), (631, 317)],
                [(638, 344), (646, 343), (644, 348), (638, 347)],
                [(632, 331), (636, 331), (636, 338), (632, 337)],
            ],
            neighbors=["bal", "ceu", "fra"],
        ),"""
assert old_ita in code, "old_ita not found"
code = code.replace(old_ita, new_ita)

old_pol = """        Country(
            id="pol",
            name="Polen",
            population=58_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(672, 289),
            polygons=[
                [(680, 261), (683, 262), (687, 272), (679, 276), (677, 280), (677, 286), (683, 288), (679, 300), (695, 302), (698, 309), (694, 319), (681, 316), (678, 310), (670, 306), (662, 310), (661, 314), (650, 310), (652, 307), (648, 301), (655, 296), (651, 281), (658, 277), (666, 278), (668, 270), (672, 268), (671, 264), (679, 262)],
            ],
            neighbors=["bal", "deu", "fin", "ukr"],
        ),"""

new_pol = """        Country(
            id="pol",
            name="Polen",
            population=58_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(664, 286),
            polygons=[
                [(647, 278), (657, 277), (666, 277), (672, 268), (684, 270), (686, 280), (680, 288), (678, 299), (670, 306), (664, 305), (649, 304), (652, 292), (650, 282), (647, 278)],
            ],
            neighbors=["blt", "ceu", "deu", "ukr"],
        ),
        Country(
            id="blt",
            name="Baltikum",
            population=6_000_000,
            climate=Climate.COLD,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(680, 258),
            polygons=[
                [(672, 268), (684, 270), (690, 262), (692, 252), (685, 247), (676, 251), (672, 260), (672, 268)],
            ],
            neighbors=["fin", "pol", "rus"],
        ),"""
assert old_pol in code, "old_pol not found"
code = code.replace(old_pol, new_pol)

old_bal = """        Country(
            id="bal",
            name="Balkan",
            population=60_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(679, 320),
            polygons=[
                [(669, 306), (677, 310), (682, 318), (692, 319), (693, 321), (685, 325), (686, 321), (682, 323), (681, 325), (687, 327), (686, 330), (678, 333), (668, 323), (668, 319), (661, 312)],
            ],
            neighbors=["deu", "ita", "pol", "tur", "ukr"],
        ),"""

new_bal = """        Country(
            id="bal",
            name="Balkan",
            population=60_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(678, 322),
            polygons=[
                [(668, 316), (669, 310), (678, 311), (688, 313), (694, 319), (692, 325), (687, 327), (686, 332), (679, 334), (668, 325), (664, 323), (658, 318), (668, 316)],
            ],
            neighbors=["ceu", "ita", "tur", "ukr"],
        ),"""
assert old_bal in code, "old_bal not found"
code = code.replace(old_bal, new_bal)

old_fin = 'neighbors=["pol", "rus", "sca"],'
new_fin = 'neighbors=["blt", "rus", "sca"],'
assert old_fin in code, "old_fin not found"
code = code.replace(old_fin, new_fin)

old_ukr = """        Country(
            id="ukr",
            name="Ukraine",
            population=52_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(699, 291),
            polygons=[
                [(687, 270), (697, 273), (705, 281), (705, 285), (713, 291), (727, 295), (726, 299), (714, 305), (719, 308), (711, 310), (704, 304), (698, 308), (697, 303), (691, 299), (679, 299), (685, 288), (679, 287), (678, 279), (688, 273), (687, 271)],
            ],
            neighbors=["bal", "pol", "rus", "tur"],
        ),"""

new_ukr = """        Country(
            id="ukr",
            name="Ukraine",
            population=52_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(699, 291),
            polygons=[
                [(684, 270), (697, 273), (706, 281), (713, 291), (727, 295), (726, 300), (714, 305), (712, 310), (704, 305), (694, 319), (688, 313), (678, 311), (669, 310), (670, 306), (678, 299), (680, 288), (686, 280), (684, 270)],
            ],
            neighbors=["bal", "ceu", "pol", "rus", "tur"],
        ),"""
assert old_ukr in code, "old_ukr not found"
code = code.replace(old_ukr, new_ukr)

old_rus_neighbors = 'neighbors=["chn", "fin", "kaz", "mon", "sca", "ukr"],'
new_rus_neighbors = 'neighbors=["blt", "chn", "fin", "kaz", "mon", "sca", "ukr"],'
assert old_rus_neighbors in code, "old_rus_neighbors not found"
code = code.replace(old_rus_neighbors, new_rus_neighbors)

old_rus_dip = '(748, 292), (749, 298), (754, 302), (752, 308), (764, 320), (760, 323), (754, 322), (747, 315), (729, 313), (721, 308), (728, 298), (727, 294)'
new_rus_dip = '(748, 292), (738, 293), (727, 294)'
assert old_rus_dip in code, "old_rus_dip not found"
code = code.replace(old_rus_dip, new_rus_dip)

old_chl = """        Country(
            id="chl",
            name="Chile",
            population=19_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(383, 542),
            polygons=[
                [(373, 532), (393, 532), (393, 552), (373, 552)],
            ],
            neighbors=["arg", "bol", "per"],
        ),"""

new_chl = """        Country(
            id="chl",
            name="Chile",
            population=19_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.RICH,
            has_airport=True,
            has_seaport=True,
            capital_pos=(381, 518),
            polygons=[
                [(378, 445), (385, 452), (388, 474), (387, 512), (383, 521), (386, 525), (384, 535), (387, 540), (391, 541), (385, 543), (387, 544), (383, 550), (387, 552), (383, 553), (394, 567), (393, 570), (386, 568), (377, 548), (376, 520), (376, 480), (375, 452), (378, 445)],
            ],
            neighbors=["arg", "bol", "per"],
        ),"""
assert old_chl in code, "old_chl not found"
code = code.replace(old_chl, new_chl)

old_tur = """        Country(
            id="tur",
            name="Türkei",
            population=95_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(707, 317),
            polygons=[
                [(697, 307), (717, 307), (717, 327), (697, 327)],
            ],
            neighbors=["bal", "irn", "mde", "ukr"],
        ),"""

new_tur = """        Country(
            id="tur",
            name="Türkei",
            population=95_000_000,
            climate=Climate.TEMPERATE,
            wealth=Wealth.MEDIUM,
            has_airport=True,
            has_seaport=True,
            capital_pos=(710, 320),
            polygons=[
                [(694, 319), (704, 316), (718, 314), (730, 316), (734, 323), (724, 326), (714, 327), (702, 326), (696, 323)],
            ],
            neighbors=["bal", "irn", "mde", "ukr"],
        ),"""
assert old_tur in code, "old_tur not found"
code = code.replace(old_tur, new_tur)

old_nab = "[(620, 332), (634, 332), (633, 341), (640, 347), (644, 344), (642, 343), (644, 340), (669, 349), (675, 343), (687, 343), (689, 374), (685, 385), (681, 387), (679, 383), (663, 373), (649, 389), (627, 389), (621, 392), (617, 390), (625, 385), (625, 379), (592, 362), (586, 362), (571, 374), (558, 376), (558, 368), (565, 360), (579, 351), (582, 343), (584, 346), (598, 344), (599, 336), (619, 333)],"
new_nab = "[(578, 345), (598, 344), (618, 343), (628, 342), (633, 346), (642, 348), (669, 349), (675, 345), (687, 345), (689, 374), (685, 385), (681, 387), (679, 383), (663, 373), (649, 389), (627, 389), (621, 392), (617, 390), (625, 385), (625, 379), (592, 362), (586, 362), (571, 374), (558, 376), (558, 368), (565, 360), (578, 345)],"
assert old_nab in code, "old_nab not found"
code = code.replace(old_nab, new_nab)

old_egy = "[(689, 346), (717, 347), (718, 359), (727, 370), (689, 370)],"
new_egy = "[(687, 345), (714, 346), (718, 353), (723, 355), (726, 368), (718, 371), (689, 371), (687, 345)],"
assert old_egy in code, "old_egy not found"
code = code.replace(old_egy, new_egy)

old_mdg = """        Country(
            id="mdg",
            name="Madagaskar",
            population=29_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(763, 471),
            polygons=[
                [(767, 453), (771, 454), (773, 462), (764, 480), (782, 479), (788, 482), (762, 482), (759, 486), (749, 485), (747, 477), (751, 471), (750, 465), (762, 459)],
            ],
            neighbors=["zaf"],
        ),"""

new_mdg = """        Country(
            id="mdg",
            name="Madagaskar",
            population=29_000_000,
            climate=Climate.HUMID,
            wealth=Wealth.POOR,
            has_airport=True,
            has_seaport=True,
            capital_pos=(764, 470),
            polygons=[
                [(765, 454), (774, 458), (776, 468), (772, 478), (764, 486), (756, 486), (750, 480), (752, 470), (758, 460), (765, 454)],
            ],
            neighbors=["zaf"],
        ),"""
assert old_mdg in code, "old_mdg not found"
code = code.replace(old_mdg, new_mdg)

with open('src/py_plaque_inc/map/geo_data.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: geo_data.py updated with 51 territories!")
