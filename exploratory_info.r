pacman::p_load("jsonlite", "dplyr", "ggplot2")

data <- read_json("./scrapping/info_all.json")
source("extra_functions.r", encoding = "UTF-8")

x <- 0:5
y <- 0:5
score_df <- expand.grid(x, y) %>%
    cbind(., rep(0, length(x) * length(y))) %>%
    rename_all(~ c("x", "y", "n"))
league_example <- names(data)[1]

for (i in names(data[[league_example]])) {
    info <- data[[league_example]][[i]]
    home <- min(info[["home_score"]], 5)
    away <- min(info[["away_score"]], 5)
    index <- home + 6 * away + 1
    score_df[index, "n"] <- score_df[index, "n"] + 1
}

(ggplot(data = score_df, aes(x = `x`, y = `y`, fill = `n`)) +
    geom_tile(color = "black", lwd = 0.5) +
    xlab("Gols do time da casa") +
    ylab("Gols to time visitante") +
    scale_x_continuous(breaks = 0:5) +
    scale_y_continuous(breaks = 0:5) +
    scale_fill_gradient(low = "lightblue", high = "purple")) %>%
    style_surface(legend.position = "bottom") %>%
    coord_fixed_save_cropped(path = "assets/gols_prop.png")