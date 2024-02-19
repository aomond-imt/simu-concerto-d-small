library("ggplot2")
library("dplyr")

d <- read.csv(glue::glue("aggregated_results.csv"))
d<-d %>% filter(nb_deps_seq == 5)
d<-d %>% filter(is_pipeline == "False")
d<-d %>% filter(nb_chains == 1)
d<-d %>% filter(topology == "clique")
dodge <- 0.9
ggplot(d, aes(x=chains_length, y=duration_mean, fill=type_comms, label=sprintf("%0.2f", duration_mean))) +
    geom_bar(color="black", stat = "identity", position= "dodge") +
    geom_errorbar(position=position_dodge(dodge), aes(ymin=duration_mean - duration_std, ymax=duration_mean + duration_std), width=.2, linewidth=1) +
    geom_text(aes(y=min(duration_mean)/2), fill="white", fontface="bold", position=position_dodge(width=dodge)) +
    ylab(glue::glue("Accumulated energy consumption (J)")) +
    theme(axis.text.y = element_text()) +
    xlab(element_blank()) +
    labs(fill="Service topology:") +
    theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5))
ggsave(glue::glue("plots/plot.pdf"), width=9, height=6)
warnings()
