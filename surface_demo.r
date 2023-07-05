pacman::p_load("ggplot2", "dplyr", "tidyr", "hrbrthemes")
source("extra_functions.r", encoding = "UTF-8")

x <- 0:5
y <- 0:5
k <- 0
size <- length(x) * length(y)

casa <- numeric(size)
visitante <- numeric(size)
empate <- numeric(size)
ambos <- numeric(size)
spread <- numeric(size)
over_under <- numeric(size)

for (i in x) {
    for (j in y) {
        index <- length(x) * i + j + 1

        if (i == j) {
            empate[index] <- 1
        } else if (i > j) {
            casa[index] <- 1
        } else if (i < j) {
            visitante[index] <- 1
        }
        if (i != 0 & j != 0) {
            ambos[index] <- 1
        }
        if (i - 2 > j) {
            spread[index] <- 1
        }
        if (i + j > 2.5) {
            over_under[index] <- 1
        }
    }
}

partition_example <- expand.grid(y, x) %>%
    rename_all(~ c("y", "x"))
partition_example["Vitória do time da casa"] <- casa
partition_example["Empate"] <- empate
partition_example["Vitória do time visitante"] <- visitante
partition_example["Ambos Marcam"] <- ambos
partition_example["Spread"] <- spread
partition_example["Total de Gols"] <- over_under
partition_example <- partition_example %>%
    pivot_longer(
        cols = !c("x", "y"),
        names_to = "Mercado",
        values_to = "Probabilidade"
    )

partition_example["Mercado"] <- factor(partition_example[["Mercado"]], levels = c("Vitória do time da casa", "Empate", "Vitória do time visitante", "Total de Gols", "Ambos Marcam", "Spread"))


(ggplot(
    data = partition_example,
    aes(x = `x`, y = `y`, fill = `Probabilidade`)
) +
    geom_tile(color = "black") +
    facet_wrap(vars(Mercado)) +
    scale_x_continuous(breaks = 0:5) +
    scale_y_continuous(breaks = 0:5) +
    scale_fill_gradient(low = "grey", high = "steelblue") +
    coord_fixed() +
    xlab("Gols to time da casa") +
    ylab("Gols do time visitante")) %>%
    style_surface(legend.position = "none") %>%
    coord_fixed_save_cropped(
        path = "assets/surface_demo.png",
        offset_down = 392 + 350, offset_up = 350
    )