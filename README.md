pokerBot
========

Reinforcement Learning for poker

Currently implements a moderately accurate simulation of a texas hold'em poker game
with a number of automated players and a human player.

Automated players include:
 dumb - always bets
 qActor - discrete state Q learning reinforcement learner for preflop betting
 nnActor - neural network based continuous state Q learning reinforcement learner for preflop betting.
