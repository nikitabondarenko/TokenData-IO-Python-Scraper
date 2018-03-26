#set working directory
setwd("C:/Users/bonda/Desktop/TokenData-IO-Python-Scraper")
install.packages('zoo')
install.packages('gclus')
library(zoo)
tokendata = data.frame(read.csv("dataTokenAdvance.csv"))
options(digits=4)

removeFinalx <- function(Y){
  Z = as.character(Y)
  return( as.double(substr(Z, 1, nchar(Z)-1)) )
}


#get rid of trailing x in columns
tokendata$btc_return = removeFinalx(tokendata$btc_return)
tokendata$eth_return = removeFinalx(tokendata$eth_return)
tokendata$token.btc_return = removeFinalx(tokendata$token.btc_return)
tokendata$token.eth_return = removeFinalx(tokendata$token.eth_return)
tokendata$token_return = removeFinalx(tokendata$token_return)
#add months since offering
tokendata$months_since = (as.yearmon("Mar 2018","%b %Y") - as.yearmon(tokendata$month,"%b %Y"))*12


#analysis
fit_btc_return <- lm(btc_return ~ current_token_price+ token.btc_return + token.eth_return + token_return + token_sale_price + usd_raised + months_since, data=tokendata)
fit_eth_return <- lm(eth_return ~ current_token_price+ token.btc_returnc + token.eth_return + token_return + token_sale_price + usd_raised + months_since, data=tokendata)

#without current token price
fit_btc_return <- lm(btc_return ~ token.btc_return + token.eth_return + token_return + token_sale_price + usd_raised + months_since, data=tokendata)
fit_eth_return <- lm(eth_return ~ token.btc_return + token.eth_return + token_return + token_sale_price + usd_raised + months_since, data=tokendata)
summary(fit_btc_return)
summary(fit_eth_return)


lm1 <- lm(token.btc_return ~ btc_return + token_sale_price + usd_raised + months_since, data=tokendata)
summary(lm1)
lm2 <- lm(token.eth_return ~ eth_return + token_sale_price + usd_raised + months_since, data=tokendata)
summary(lm2)


df = tokendata
library(gclus)
dta <- df[c(1,6,8,10,11)] # get data 
dta = dta[complete.cases(dta), ]
dta.r <- abs(cor(dta)) # get correlations
dta.col <- dmat.color(dta.r) # get colors
cpairs(dta, panel.colors=dta.col, gap=.5, main="Variables Ordered and Colored by Correlation" )


