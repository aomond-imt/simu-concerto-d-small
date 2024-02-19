library("ggplot2")
library("dplyr")

d <- read.csv(glue::glue("results.csv"))
d<-d %>% filter(id_run == 0)
d<-d %>% filter(nb_deps_seq == 5)
ggplot(d, aes(x=chains_length, y=dynamic, fill=type_comms, label=sprintf("%0.2f", dynamic))) +
    geom_bar(color="black", stat = "identity", position = "dodge") +
    geom_text(aes(y=min(dynamic)/2), fill="white", fontface="bold", position=position_dodge(width=0.9)) +
    ylab(glue::glue("Accumulated energy consumption (J)")) +
    theme(axis.text.y = element_text()) +
    xlab(element_blank()) +
    labs(fill="Service topology:") +
    theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5))
ggsave(glue::glue("plots/plot.pdf"), width=9, height=6)
warnings()
