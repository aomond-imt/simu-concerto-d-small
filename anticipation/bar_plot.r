library("ggplot2")
library("dplyr")

d <- read.csv(glue::glue("aggregated_results.csv"))
d<-d %>% filter(nb_deps_seq == 5)
# d<-d %>% filter(is_pipeline == "False")
d<-d %>% filter(nb_chains == 1)
d<-d %>% filter(topology == "star")
dodge <- 1.9
mean <- d$dynamic_mean
std <- d$dynamic_std

ggplot(d, aes(x=chains_length, y=mean, fill=type_comms, label=sprintf("%0.2f", mean))) +
    geom_bar(color="black", stat = "identity", position= "dodge") +
    # geom_errorbar(position=position_dodge(dodge), aes(ymin=mean - std, ymax=mean + std), width=.2, linewidth=1) +
    # geom_text(aes(y=min(mean)/2), fill="white", fontface="bold", position=position_dodge(width=dodge)) +
    geom_text(vjust=-1, fill="white", fontface="bold", position=position_dodge(width=dodge)) +
    scale_x_continuous(breaks=unique(d$chains_length)) +
    ylab(glue::glue("Accumulated energy consumption (J)")) +
    # ylab(glue::glue("Duration (h)")) +
    theme(axis.text.y = element_text()) +
    xlab(element_blank()) +
    facet_wrap(~ is_pipeline)
    labs(fill="Service topology:") +
    theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5))
ggsave(glue::glue("plots/plot.pdf"), width=9, height=6)
warnings()
