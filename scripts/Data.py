from matplotlib import pyplot as plt

def graph(S_speeds, S_ranges, S_autos, S_sexes, S_popul, W_speeds, W_ranges, W_autos, W_sexes, W_popul):
    frames = len(S_speeds)
    x_values = []
    i = 0
    while i < frames:
        i+=1
        x_values.append(i)

    plt.plot(x_values, S_speeds)
    plt.plot(x_values, S_ranges)
    plt.plot(x_values, S_autos)
    plt.plot(x_values, S_sexes)
    plt.plot(x_values, S_popul)
    plt.plot(x_values, W_speeds)
    plt.plot(x_values, W_ranges)
    plt.plot(x_values, W_autos)
    plt.plot(x_values, W_sexes)
    plt.plot(x_values, W_popul)
    plt.title("Sheeps")
    plt.show()
    
graph()
