import sys
import random as rng
import time

M = 0
P = 0
G = []
h_arrs = []
colls = 0
rows = 0
elapsed_time = 0
##################### Encoding / decoding #################

# funkcija generuojančios matricos generavimui
def create_gen_matrix():
    global rows, colls
    rows = M + 1
    colls = 2**M

    for i in range(rows):
        G.append([0] * colls)

    reps = colls // 2

    for i in range(rows):
        if i == 0:
            for j in range(colls):
                G[i][j] = 1
        else:
            index = 0

            for k in range(int(reps)):
                for l in range(2**(i-1)):
                    G[i][index] = 0
                    index = index + 1

                for l in range(2**(i-1)):
                    G[i][index] = 1
                    index = index + 1
            reps /= 2

# funkcija vektoriaus kodavimui
# parametras - vektorius
# gražina - užkoduotą vektorių
def encode_vector(vector):
    size = 2**M

    encoded_vector = [0] * size
    for i in range(size):
        for j in range(len(vector)):
            encoded_vector[i] += vector[j] * G[j][i]
        encoded_vector[i] = encoded_vector[i] % 2

    return encoded_vector


# funkcija, realizuojanti kanalą
# parametras - užkoduotas vektorius
# gražina - iškraipytą vektorių
def channel(vector):

    distorted_vector = vector.copy()

    for i in range(len(vector)):
        random = rng.random()
        if random <= P:
            distorted_vector[i] = swap(vector[i])

    return distorted_vector

# funkcija bitų apvertimui
# parametras - bitas
# gražina - priešingą bitą
def swap(x):
    if x == 1:
        y = 0
    elif x == 0:
        y = 1
    return y

# funkcija wm skaičiavimui
# parametras - iš kanalo išėjęs vektorius
# gražina - wm
def create_wm(w):
    global colls, h_arrs

    w_arr = [[] for _ in range(M + 1)]

    for i in range(colls):
        if w[i] == 0:
            w[i] = -1

    w_arr[0] = w

    # daugyba wi-1 x Hi
    for i in range(1, M + 1):
        w_arr[i] = [0] * 2**M
        
        for j in range(2**M):
            for k in range(2**M):
                w_arr[i][j] += w_arr[i - 1][k] * h_arrs[i - 1][k][j]

    return w_arr[M]

# funkcija, generuojanti Hadamardo matricas ir sudedanti jas į sąrašą
def create_H_matrices():
    h = [[1, 1], [1, -1]]

    # ciklas, kuris sukasi tiek, kiek reikia matricų
    for k in range(1, M + 1):
        x = 2**(M - k)
        y = 2**(k - 1)

        # inicializuojamos matricos, gaunamos dviejuose daugybos I2m-i x H X I2^(i-1) žingsniuose
        ih = [[0] * (2 * x) for _ in range(2 * x)]
        hi = [[0] * (2 * x * y) for _ in range(2 * x * y)]

        # atliekamas algoritmas, atitinkantis pirmąjį daugybos žingsnį
        if x != 1:
            for i in range((2 * x) - 1):
                for j in range((2 * x) - 1):
                    if i == j and i % 2 == 0 and i != (2 * x) - 1:
                        ih[i][j] = 1
                        ih[i][j + 1] = 1
                        ih[i + 1][j] = 1
                        ih[i + 1][j + 1] = -1
        else:
            ih = h

        # atliekamas algoritmas, atitinkantis antrąjį daugybos žingsnį
        if y != 1:
            for i in range(2 * x):
                for j in range(2 * x):
                    if ih[i][j] == 1:
                        for l in range(y):
                            hi[(i * y) + l][(j * y) + l] = 1
                    elif ih[i][j] == -1:
                        for l in range(y):
                            hi[(i * y) + l][(j * y) + l] = -1
        else:
            hi = ih


        h_arrs.append(hi)

# dekodavimo funkcija
# parametras - iš kanalo išėjęs vektorius
# gražina - dekoduotą vektorių
def decode(w):

    wm = create_wm(w)

    max_index = 0
    max_val = -1
    sign = 1

    # ieškoma didžiausios wm vektoriaus absoliučiosios reikšmės bei jos ženklo
    for i in range(len(wm)):
        if abs(wm[i]) > abs(max_val):
            max_val = wm[i]
            max_index = i
            if wm[i] < 0:
                sign = 0
            else:
                sign = 1

    max_bin = format(max_index, "b")

    while len(max_bin) < M:
        max_bin = "0" + max_bin

    word = max_bin[::-1]

    # prirašomas atitinkamas bitas pagal ženklą
    if sign == 0:
        word = "0" + word
    else:
        word = "1" + word

    word_as_vector = []

    # patogumui vektorius iš stringo verčiamas į sarašą
    for i in range(len(word)):
        word_as_vector.append(int(word[i]))

    return word_as_vector

####################### Utility functions ###################

# funkcija, atliekanti programos pradinį darbą
def initialize():
    global M, P

    M = int(input("Enter m: "))
    P = float(input("Enter mistake probability: "))

    create_gen_matrix()
    create_H_matrices()

# funkcija, verčianti tekstą į vektorių sąrašą
# parametras - tekstas
# gražina - vektorių sąrašą
def text_to_vectors(string):
    size = 2**M
    vectors = []

    # tekstas verčiamas į simbolių sąrašą,
    char_list = list(string)

    # į pagal ascii atitinkančių dešimtainių reikšmių sąrašą,
    ascii_list = [ord(char) for char in char_list]

    # į dvejetainių reikšmių sąrašą,
    binary_list = [bin(ascii)[2:].zfill(7) for ascii in ascii_list]
    
    # sąrašas verčiamas į vieno lygio sąrašą
    binary_digits = [int(digit) for binary in binary_list for digit in binary]

    # sąrašas verčiamas į reikiamo ilgio vektorių sąraša
    for i in range(0, len(binary_digits), M+1):
        sublist = binary_digits[i:i+M+1]
        # jei paskutiniam vektoriui trūksta bitų, prirašomas reikalingas kiekis nulių
        sublist += [0] * (M+1 - len(sublist))

        vectors.append(sublist)

    return vectors

# funkcija vektorių sąrašo kodavimui
# parametras - vektorių sąrašas
# gražina - užkoduotų vektorių sąrašą
def encode_vectors(vector_list):
    encoded_vectors = []

    for i in range(0, len(vector_list)):
        encoded_vectors.append(encode_vector(vector_list[i]))

    return encoded_vectors

# funkcija, verčianti vektorių sąrašą į tekstą
# parametras - dekoduotų vektorių sąrašas
# gražina - tekstą
def vectors_to_text(vectors):
    # vektorių sąrašas verčiamas į vieno lygio sąrašą
    binary_digits = [digit for vector in vectors for digit in vector]

    # sąrašo nariai surašomi į vieną stringą
    binary_string = ''.join(str(digit) for digit in binary_digits)

    # sudaromas stringų po 7 bitus, reprezentuojančius po vieną simbolį sąrašas
    bin_chars = []
    for i in range(0, len(binary_string), 7):
        bin_chars.append(binary_string[i:i + 7])

    # kiekvienas bitų stringas verčiamas į ascii simbolį
    ascii_chars = [chr(int(''.join(bin_char), 2)) for bin_char in bin_chars]
    
    # simboliai sudedami į vieną stringą
    ascii_string = ''.join(ascii_chars)

    print(ascii_string)

    return ascii_string

# funkcija, tikrinantim kiek bei kuriose pozicijose atlikta klaidų
# parametrai - užkoduotas vektorius, iš kanalo išėjęs vektorius
def check_mistakes(enc_vector, rec_vector):
    positions = []
    mistakes = 0

    for i in range(len(enc_vector)):
        if enc_vector[i] != rec_vector[i]:
            positions.append(i)
            mistakes += 1

    if mistakes != 0:
        print("\n" + str(mistakes) + " mistakes were made in positions:")

    for i in range(len(positions)):
        if i != len(positions) - 1:
            sys.stdout.write(str(positions[i]) + ", ")

        else:
            sys.stdout.write(str(positions[i]))

    sys.stdout.write("\n")
    sys.stdout.flush()

# funkcija rankiniam iš kanalo išėjusio vektoriaus klaidų darymui / taisymui
# parametras - iš kanalo išėjęs vektorius
# gražina - pakeistą vektorių
def manual_edit(vector):
    edited_vector = []
    positions=[]
    edit_choice = (input("\nDo you wish to edit the vector?: [y/n]\n"))

    if edit_choice == "y":
        pos_str = input("\nEnter positions to edit separated by commas:\n")
        positions = pos_str.split(",")

    for i in range(len(vector)):
        if str(i) in positions:
            edited_vector.append(swap(vector[i]))
        else:
            edited_vector.append(vector[i])

    print("\nEdited vector:")
    print(edited_vector)
    return edited_vector

def current_milli_time():
    return round(time.time() * 1000)

############################ Scenarios ############################

# funkcija scenarijaus pasirinkimui
def select_scenario():
    scen = int(input("\nSelect input: \n1. Vector \n2. Text\n"))
    if scen == 1:
        vector_scen()
    elif scen == 2:
        text_scen()

# funkcija atlikti vektoriaus kodavimo scenarijui
def vector_scen():

    vector = []
    vector_str = input("\nEnter vector:\n")

    for i in vector_str:
        if i == "1" or i == "0":
            vector.append(int(i))

    # tikrinamas vektoriaus ilgis
    if len(vector) != M + 1:
        print("Vector must be of length M + 1!")
        if vector_scen() == -1:
            return -1

    print(vector)

    encoded_vector = encode_vector(vector)
    print("\nEncoded vector:")
    print(encoded_vector)

    received_vector = channel(encoded_vector)
    print("\nVector received from channel:")
    print(received_vector)

    check_mistakes(encoded_vector, received_vector)
    edited_vector = manual_edit(received_vector)

    # start_time = time.perf_counter()
    # print(start_time)
    decoded_vector = decode(edited_vector)
    # end_time = time.perf_counter()
    # print(end_time)
    
    print("\nDecoded vector:")
    print(decoded_vector)

    return -1

# funkcija atlikti teksto kodavimo scenarijui
def text_scen():
    text = ''

    print("\nEnter text, use CTRL+Z as the last line to finish: \n")

    while True:
        try:
            line = input()
        except EOFError:
            break
        text += line + "\n"

    vectors = text_to_vectors(text)

    # be kodavimo
    received_vectors = []

    for i in range(len(vectors)):
        received_vectors.append(channel(vectors[i]))

    print("\nText received from channel without encoding:")

    vectors_to_text(received_vectors)

    # su kodavimu

    received_vectors = []

    encoded_vectors = encode_vectors(vectors)

    for i in range(len(encoded_vectors)):
        received_vectors.append(channel(encoded_vectors[i]))

    decoded_vectors = []

    for i in range(len(encoded_vectors)):
        decoded_vectors.append(decode(received_vectors[i]))

    print("\nText received from channel after encoding:")

    vectors_to_text(decoded_vectors)


def main():
    initialize()
    select_scenario()
    
    print("\nPress Enter to exit")
    input()

main()
