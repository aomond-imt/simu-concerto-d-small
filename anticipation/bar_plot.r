library("ggplot2")
library("dplyr")

d <- read.csv(glue::glue("results_clique_star_chain.csv"))
a <- aggregate(d$dynamic, by=list(d$type_comms, d$nb_deps_seq, d$nb_nodes, d$topology, d$routing), FUN=mean)
b <- aggregate(d$dynamic, by=list(d$type_comms, d$nb_deps_seq, d$nb_nodes, d$topology, d$routing), FUN=sd)
a <- cbind(a, std = b$x)
colnames(a) <- c("type_comms", "nb_deps_seq", "nb_nodes", "topology", "routing", "mean", "std")

dodge <- 1
ggplot(a, aes(x=nb_nodes, y=mean, fill=type_comms, label=sprintf("%0.2f", mean))) +
    geom_bar(color="black", stat = "identity", position= "dodge") +
    # geom_errorbar(position=position_dodge(dodge), aes(ymin=mean - std, ymax=mean + std), width=.2, linewidth=1) +
    # geom_text(aes(y=min(mean)/2), fill="white", fontface="bold", position=position_dodge(width=dodge)) +
    geom_text(vjust=-1, fill="white", fontface="bold", position=position_dodge(width=dodge)) +
    ylab(glue::glue("Accumulated energy consumption (J)")) +
    # ylab(glue::glue("Duration (h)")) +
    scale_x_continuous(breaks=unique(a$nb_nodes)) +
    facet_wrap(~ topology) +
    theme(axis.text.y = element_text()) +
    xlab(element_blank()) +
    labs(fill="Service topology:") +
    theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5))
ggsave(glue::glue("plots/plot.pdf"), width=9, height=6)
warnings()
