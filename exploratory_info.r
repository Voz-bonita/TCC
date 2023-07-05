pacman::p_load("jsonlite", "dplyr", "ggplot2")

data <- read_json("./scrapping/info_all.json")
source("extra_functions.r", encoding = "UTF-8")

x <- 0:5
y <- 0:5
size <- length(x) * length(y)
score_df <- expand.grid(x, y) %>%
    cbind(., rep(0, size)) %>%
    cbind(., rep(names(data), each = size)) %>%
    rename_all(~ c("x", "y", "Proporção", "league"))
league_example <- names(data)[1]

for (league in names(data)) {
    league_index <- which(names(data) == league)
    n_max <- length(data[[league]])
    for (game in names(data[[league]])) {
        info <- data[[league]][[game]]
        home <- min(info[["home_score"]], 5)
        away <- min(info[["away_score"]], 5)
        index <- (home + 6 * away + 1) + (league_index - 1) * size
        score_df[index, "Proporção"] <- score_df[index, "Proporção"] + 1 / n_max
    }
}

(ggplot(data = score_df, aes(x = `x`, y = `y`, fill = `Proporção`)) +
    geom_tile(color = "black", lwd = 0.5) +
    facet_wrap(vars(league)) +
    xlab("Gols do time da casa") +
    ylab("Gols to time visitante") +
    scale_x_continuous(breaks = 0:5) +
    scale_y_continuous(breaks = 0:5) +
    scale_fill_gradient(low = "#5a5151", high = "orange")) %>%
    style_surface(legend.position = "bottom") %>%
    coord_fixed_save_cropped(
        path = "assets/gols_prop.png",
        offset_up = 0, offset_down = 0
    )