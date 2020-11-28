package main

/* a script to predict minecraft enchantments iirc */

import (
	"fmt"
	"math/rand"
)

const (
	numEnchants                  = 136
	desiredWeight                = 2
	conflictingEnchantmentWeight = 1
)

/* Did we get the desired enchant? */
func enchant(modifiedLevel int) bool {
	tmp := rand.Intn(numEnchants)
	if tmp < conflictingEnchantmentWeight {
		return false
	} else if tmp < (conflictingEnchantmentWeight + desiredWeight) {
		return true
	}

	for rand.Intn(50) < (modifiedLevel + 1) {
		tmp = rand.Intn(numEnchants)
		if tmp < conflictingEnchantmentWeight {
			return false
		} else if tmp < (conflictingEnchantmentWeight + desiredWeight) {
			return true
		}

		modifiedLevel = modifiedLevel / 2
	}

	return false
}

func test(numTimes int) float64 {
	total := 0
	for i := 0; i < numTimes; i++ {
		if enchant(31) {
			total = total + 1
		}
	}

	return float64(total) / float64(numTimes)
}

func main() {
	fmt.Println("Probability of getting a mending book: ", 0.019*test(10000000))
}
