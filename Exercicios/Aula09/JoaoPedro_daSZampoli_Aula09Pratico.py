import numpy as np

def FitnessFunction(x):
    return 1 + 2*x - x**2                       # Exemplo de função a ser otimizada (Também é a função do exemplo do slide)

MaxInterations = 100                            # Número máximo de iterações
Particles = 5                                   # Número de partículas
Boundaries = np.array([[-10, 10]])              # Limites do espaço de busca
InertiaWeight = 0.7                             # Peso de inércia
C1 = 0.2                                        # Coeficiente/Peso cognitivo 1
C2 = 0.6                                        # Coeficiente/Peso cognitivo 2
R1 = 0.4657                                     # Número aleatório 1
R2 = 0.5319                                     # Número aleatório 2


# PSO
def PSO(FunctionInput, Boundaries, Particles, MaxInterations, InertiaWeight, C1, C2, R1, R2):
    # Inicialização das posições
    Dimensions = 1

    # Usando caso do slide
    XInit = np.array([0.4657, 0.8956, 0.3877, 0.4902, 0.5039])
    VInit = np.array([0.5319, 0.8185, 0.8331, 0.7677, 0.1708])

    Positions = 10 * (XInit - 0.5)
    Velocity = VInit - 0.5

    Positions = Positions.reshape(Particles, Dimensions)
    Velocity = Velocity.reshape(Particles, Dimensions)
    

    # Positions = np.random.uniform(Boundaries[:, 0], Boundaries[:, 1], (Particles, len(Boundaries)))   # No caso de inicialização aleatória
    # Velocity = np.zeros((Particles, Dimensions))                                                      # No caso de inicialização aleatória
    PBest = Positions.copy()
    PBestValue = np.array([FunctionInput(p[0]) for p in Positions])
    GBest = PBest[np.argmax(PBestValue)]
    GBestValue = np.max(PBestValue)

    print("\nValores Iniciais (PSO):")
    print("Posições: ", Positions.flatten())
    print("Velocidades: ", Velocity.flatten())
    print("Valores do Fitness: ", PBestValue)
    print("Melhor Posição Global: ", GBest)
    print("Melhor Fitness Global: ", GBestValue)

    for i in range(MaxInterations):
        NewVelocity = Velocity.copy()
        NewPositions = Positions.copy()

        for j in range(Particles):
            NewVelocity[j] = (InertiaWeight * Velocity[j] + C1 * R1 * (PBest[j] - Positions[j]) + C2 * R2 * (GBest - Positions[j]))

        for j in range(Particles):
            NewPositions[j] = Positions[j] + NewVelocity[j]
            NewPositions[j] = np.clip(NewPositions[j], Boundaries[:,0], Boundaries[:,1])
        
        Velocity = NewVelocity
        Positions = NewPositions

        for j in range(Particles):
            fitness = FunctionInput(Positions[j][0])
            if fitness > PBestValue[j]:
                PBest[j] = Positions[j]
                PBestValue[j] = fitness
                if fitness > GBestValue:
                    GBest = Positions[j]
                    GBestValue = fitness

        # Print de Iterações só pra exemplificar
        if i < 3:  # Alterável, só deixei assim para não poluir o terminal nos testes
            print(f"\nIteração {i+1}:")
            print("Posições: ", Positions.flatten())
            print("Velocidades: ", Velocity.flatten())
            print("Valores do Fitness: ", [FunctionInput(p[0]) for p in Positions])
            print("Melhor Posição Pessoal: ", PBest.flatten())
            print("Melhor Valor Pessoal: ", PBestValue)
            print("Melhor Posição Global: ", GBest)
            print("Melhor Fitness Global: ", GBestValue)


    print("\n\nMelhor posição: ", GBest)
    print("Melho valor da função: ", GBestValue)

def ACO(MatrizDistribuicao, IndiceVerticeInicial, Alpha=1, Beta=1, Rho=0.5, Tau0=2):
    N = MatrizDistribuicao.shape[0]
    Tau = np.full_like(MatrizDistribuicao, Tau0, dtype=float)
    np.fill_diagonal(Tau, 0)

    with np.errstate(divide='ignore'):
        Eta = 1 / MatrizDistribuicao
    Eta[MatrizDistribuicao == 0] = 0

    Visitado = [IndiceVerticeInicial]
    Caminho = []
    CustoTotal = 0
    Atual = IndiceVerticeInicial

    for _ in range(N - 1):
        NaoVisitado = [i for i in range(N) if i not in Visitado]
        Numeradores = [(Tau[Atual][j] ** Alpha) * (Eta[Atual][j] ** Beta) for j in NaoVisitado]
        Denominadores = sum(Numeradores)
        Probabilidades = [num / Denominadores for num in Numeradores]
        ProximoIndice = NaoVisitado[np.argmax(Probabilidades)]
        Caminho.append((Atual, ProximoIndice))
        CustoTotal += MatrizDistribuicao[Atual][ProximoIndice]
        Visitado.append(ProximoIndice)
        Atual = ProximoIndice

    # Atualiza feromônio
    DeltaTau = np.zeros_like(Tau)
    for (i, j) in Caminho:
        delta = 1 / CustoTotal
        DeltaTau[i][j] = delta
        DeltaTau[j][i] = delta  # grafo não direcionado

    Tau = (1 - Rho) * Tau + Rho * DeltaTau

    match IndiceVerticeInicial:
        case 0:
            LetraVertice = 'A'
        case 1:
            LetraVertice = 'B'
        case 2:
            LetraVertice = 'C'
        case 3:
            LetraVertice = 'D'
        case 4:
            LetraVertice = 'E'

    def IndiceParaLetra(Indice):          # Fazendo isso daqui só pra ficar mais bonitinho na hora de printar
        Letras = ['A', 'B', 'C', 'D', 'E']
        return Letras[Indice] if 0 <= Indice < len(Letras) else str(Indice)

    print(f"\nCaminho encontrado a partir do vértice {LetraVertice}:")
    for (i, j) in Caminho:
        print(f"Vértice {IndiceParaLetra(i)} -> Vértice {IndiceParaLetra(j)} (Custo: {MatrizDistribuicao[i][j]})")
    print(f"Custo total: {CustoTotal}")
    print(f"Feromônio atualizado:\n{Tau}")

print("Selecione o tipo de algoritmo a ser visualizado:")
print("1 - Algoritmo de PSO (Particle Swarm Optimization)")
print("2 - Algoritmo de ACO (Ant Colony Optimization)")
print("3 - Sair")
Opcao = int(input("\nOpção: "))
if Opcao == 1:
    PSO(FitnessFunction, Boundaries, Particles, MaxInterations, InertiaWeight, C1, C2, R1, R2)
elif Opcao == 2:
    MatrizDistribuicao = np.array([
    [0, 2, 10, 8, 3],   # A
    [1, 0, 2, 5, 7],    # B
    [9, 1, 0, 3, 6],    # C
    [10, 4, 3, 0, 2],   # D
    [2, 7, 5, 1, 0]     # E
])
    ACO(MatrizDistribuicao, 0)
    ACO(MatrizDistribuicao, 1)
    ACO(MatrizDistribuicao, 2)
    ACO(MatrizDistribuicao, 3)
    ACO(MatrizDistribuicao, 4)
elif Opcao == 3:
    exit()
else:
    print("Opção Inválida")
