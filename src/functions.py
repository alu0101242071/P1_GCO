def readMatrix(filename): # Lee la matriz con el formato adecuado, la primera linea como valor minimo, la segunda como valor maximo y el resto de lineas como usuarios individuales
    with open(filename, "r") as matriz:
        file = matriz.read()

    lineas = file.split("\n")
    valorMin, valorMax, *valoraciones = (linea.split() for linea in lineas)

    return valoraciones, valorMin, valorMax


def sameRatedItems(user1, user2): # Devuelve un array con los indices de los items que ambos usuarios han valorado
    commonItemsIndex = []

    for i in range(len(user1)):
        if (user1[i] == '-') or (user2[i] == '-'):
            continue
        else:
            commonItemsIndex.append(i)
    
    return commonItemsIndex


def userAverage(user): # Devuelve la media del usuario sin contar los valores vacios con '-'
    intRatings = []

    for rating in user:
        if rating != '-':
            intRatings.append(float(rating))
        else:
            continue
    
    return sum(intRatings)/len(intRatings)


def commonItemArrays(user1, user2): # Devuelve los arrays de los items valorados por ambos usuarios como floats para calcular con ellos
    commonIndex = sameRatedItems(user1, user2)
    user1Float = []
    user2Float = []

    for i in commonIndex:
        user1Float.append(float(user1[i]))
        user2Float.append(float(user2[i]))

    return user1Float, user2Float


def pearsonCorelation(user1, user2): # Devuelve la correlacion de Pearson entre dos usuarios, hagan funciones similares para las otras dos con la formula de las diapos
    user1Ratings, user2Ratings = commonItemArrays(user1, user2)

    sumNumerador = 0
    sumDenominador1 = 0
    sumDenominador2 = 0

    for i in range(len(user1Ratings)):
        sumNumerador += ((user1Ratings[i] - userAverage(user1)) * (user2Ratings[i] - userAverage(user2)))
        sumDenominador1 += ((user1Ratings[i] - userAverage(user1)) ** 2)
        sumDenominador2 += ((user2Ratings[i] - userAverage(user2)) ** 2)

    return (sumNumerador / ((sumDenominador1 ** 0.5) * (sumDenominador2 ** 0.5)))


def pearsonArray(user, matrix): # Devuelve un array de tuplas de correlaciones de Pearson junto con el usuario correspondiente con el resto de usuarios de la matriz proporcionada, falta comprobacion de que el usuario esta en la matriz

    pearsonRatings = []

    for otherUser in matrix:
        if user == otherUser:
            continue

        correlation = pearsonCorelation(user, otherUser)
        pearsonRatings.append((otherUser, correlation))

    return pearsonRatings # Cada elemento del array es la lista de valoraciones del usuario como primer elemento y el segundo elemento la correlacion con el usuario original


def cosineCorelation(user1, user2):
    user1Ratings, user2Ratings = commonItemArrays(user1, user2)

    sumNumerador = 0
    sumDenominador1 = 0
    sumDenominador2 = 0

    for i in range(len(user1Ratings)):
        sumNumerador += (user1Ratings[i] * user2Ratings[i])
        sumDenominador1 += (user1Ratings[i] ** 2)
        sumDenominador2 += (user2Ratings[i] ** 2)

    return (sumNumerador / ((sumDenominador1 ** 0.5) * (sumDenominador2 ** 0.5)))

def cosineArray(user, matrix):
    cosineRatings = []

    for otherUser in matrix:
        if user == otherUser:
            continue

        correlation = cosineCorelation(user, otherUser)
        cosineRatings.append((otherUser, correlation))
    
    return cosineRatings


def euclideanCorelation(user1, user2):
    user1Ratings, user2Ratings = commonItemArrays(user1, user2)
    result = 0

    for i in range(len(user1Ratings)):
        result += ((user1Ratings[i] - user2Ratings[i]) ** 2)
    
    return (result ** 0.5)


def euclideanArray(user, matrix):
    euclideanRatings = []

    for otherUser in matrix:
        if user == otherUser:
            continue

        correlation = euclideanCorelation(user, otherUser)
        euclideanRatings.append((otherUser, correlation))

    return euclideanRatings


def similarNeighbours(user, matrix, metrica, numeroVecinos): # Devuelve un array de los vecinos más similares segun la metrica elegida y el numero de vecinos estipulado
    neighbours = []

    missing_indexes = [(i) for i in range(len(user)) if user[i] == '-']

    matrizSinIncompatibles = []

    for otherUser in matrix: # Quitamos de la matriz los otros usuarios que no tengan valorados los items que intentamos predecir del usuario
        for index in missing_indexes:
            if otherUser[index] != '-':
                matrizSinIncompatibles.append(otherUser)


    if metrica == 'pearson': # Aqui falta añadir otros dos casos de distancia coseno y distancia euclidea
        corrArray = sorted(pearsonArray(user, matrizSinIncompatibles), key=lambda x: x[1], reverse=True)
        for i in range(numeroVecinos):
            neighbours.append(corrArray[i])
    elif metrica == 'cosine':
        corrArray = sorted(cosineArray(user, matrizSinIncompatibles), key=lambda x: x[1], reverse=True)
        for i in range(numeroVecinos):
            neighbours.append(corrArray[i])
    elif metrica == 'euclidean':
        corrArray = sorted(euclideanArray(user, matrizSinIncompatibles), key=lambda x: x[1])
        for i in range(numeroVecinos):
            neighbours.append(corrArray[i])
    
    return neighbours


def calculatePredictions(matrix, metrica, numeroVecinos, tipoPrediccion, min_val, max_val): # Funcion final que devolverá la matriz rellena con las predicciones dependiendo del método usado

    for user in matrix:
        if '-' not in user:
            continue

        missing_indexes = [(i) for i in range(len(user)) if user[i] == '-'] # Indices de los elementos que tenemos que predecir, se usan para ver la valoracion de los demás usuarios de ese elemento

        if tipoPrediccion == 'simple': # Calcula la prediccion en base a la formula de prediccion simple
            sumNumerador = 0
            sumDenominador = 0
            
            for index in missing_indexes: # Bucle para que calcule todos los indices que faltan, porque puede haber mas de uno
                for otherUser in similarNeighbours(user, matrix, metrica, numeroVecinos):
                    if otherUser[0][index] == '-':
                        continue
                    sumNumerador += (otherUser[1] * float(otherUser[0][index]))
                    sumDenominador += abs(otherUser[1])
                
                if sumDenominador != 0:   
                    prediction = sumNumerador / sumDenominador
                    if prediction > float(max_val[0]): # Comprobación de que está dentro del rango
                        user[index] = float(max_val[0])
                    elif prediction < float(min_val[0]):
                        user[index] = float(min_val[0])
                    else:
                        user[index] = round(prediction, 2)
                else:
                    print("No se puede dividir por 0")

        elif tipoPrediccion == 'media': # Calcula la prediccion en base a la formula de distancia con la media
            sumNumerador = 0
            sumDenominador = 0

            for index in missing_indexes: # Bucle para que calcule todos los indices que faltan, porque puede haber mas de uno
                for otherUser in similarNeighbours(user, matrix, metrica, numeroVecinos): # Calcula para cada vecino la predicción
                    if otherUser[0][index] == '-':
                        continue
                    sumNumerador += (otherUser[1] * (float(otherUser[0][index]) - userAverage(otherUser[0])))
                    sumDenominador += abs(otherUser[1])
                
                if sumDenominador != 0:
                    prediction = userAverage(user) + (sumNumerador / sumDenominador)
                    if prediction > float(max_val[0]): # Comprobación de que está dentro del rango
                        user[index] = float(max_val[0])
                    elif prediction < float(min_val[0]):
                        user[index] = float(min_val[0])
                    else:
                        user[index] = round(prediction, 2)
                else: 
                    print("No se puede dividir por 0")

    return matrix