package main

import (
	"fmt"
	"math/rand"
)

type option struct {
	weight float64
	value  func() float64
}

func randomHelper(in float64, weight float64) (bool, float64) {
	return in <= weight, in - weight
}

func randomHelper2(lootTable []option) float64 {
	r := rand.Float64()
	for _, theOption := range lootTable {
		done := false
		done, r = randomHelper(r, theOption.weight)
		if done {
			return theOption.value()
		}
	}

	return 0.0 //lootTable[len(lootTable)-1].value()
}

func constValue(value float64) func() float64 {
	return func() float64 {
		/* because the crash factor doesn't apply to money rewards, we simply undo it. */
		return value
	}
}

func multipleWorthStatic(f func() float64, amount int) func() float64 {
	return func() float64 {
		return f() * float64(amount)
	}
}

func multipleWorth(f func() float64, amount int) func() float64 {
	return func() float64 {
		total := 0.0
		for i := 0; i < amount; i++ {
			total = total + f()
		}
		return total
	}
}

func getIronIngotWorth() float64 {
	return 300
	//return 250
}

func getGrassBlockWorth() float64 {
	return 500
	//return 400
}

func getSandBlockWorth() float64 {
	return 500
	//return 300
}

func getPigSpawnerWorth() float64 {
	return 45000
}

func getCowSpawnerWorth() float64 {
	return 150000
}

func getDiamondWorth() float64 {
	return 1750
	//return 1500
}

func getRedstoneWorth() float64 {
	return 3
}

func getDiamondPickWorth() float64 {
	return 400
}

func getIronPickWorth() float64 {
	return 150
}

func getCobblestoneStackWorth() float64 {
	return 3
}

func getEpicKeyWorth() float64 {
	// todo: figure out reasonable value
	return 60000
}

func getEliteKitWorth() float64 {
	// todo: figure out reasonable value
	return 1000
}

func getEnderChestWorth() float64 {
	// todo: figure out reasonable value
	return 500
}

func getRareKeyApparentWorth() float64 {
	return 14000
	//return 10000
}

func getCommonKeyApparentWorth() float64 {
	return 2750
	//return 1500
}

func getVoteKeyApparentWorth() float64 {
	return 700
}

func getRareKeyActualWorth() float64 {
	//return 13500
	return randomHelper2([]option{
		{0.0319, constValue(800)},
		{0.0425, constValue(1000)},
		{0.0531, constValue(1500)},
		{0.0638, constValue(2000)},
		{0.0744, constValue(3000)},
		{0.0425, multipleWorthStatic(getIronIngotWorth, 12)},
		{0.0531, multipleWorthStatic(getIronIngotWorth, 24)},
		// double check this at some point...?
		{0.0425, multipleWorthStatic(getRedstoneWorth, 64)},
		{0.0319, multipleWorthStatic(getRedstoneWorth, 64)},
		// ^
		{0.0212, multipleWorthStatic(getDiamondWorth, 3)},
		{0.0319, multipleWorthStatic(getDiamondWorth, 5)},
		{0.117, getDiamondPickWorth},
		{0.0212, multipleWorthStatic(getCobblestoneStackWorth, 4)},
		{0.0425, multipleWorthStatic(getCobblestoneStackWorth, 5)},
		{0.0638, multipleWorthStatic(getCobblestoneStackWorth, 6)},
		{0.0425, multipleWorthStatic(getGrassBlockWorth, 15)},
		{0.0212, multipleWorthStatic(getSandBlockWorth, 15)},
		{0.0319, multipleWorth(getCommonKeyWorth, 3)},
		{0.0531, multipleWorth(getRareKeyActualWorth, 2)},
		{0.0106, getEpicKeyWorth},
		{0.0106, getEliteKitWorth},
		{0.0531, getEnderChestWorth},
		{0.0319, getPigSpawnerWorth},
		{0.0106, getCowSpawnerWorth},
	})
}

func getRareKeyWorth() float64 {
	return getRareKeyApparentWorth()
}

func getCommonKeyActualWorth() float64 {
	//return 3000
	return randomHelper2([]option{
		{0.0594, constValue(300)},
		{0.0679, constValue(500)},
		{0.0764, constValue(800)},
		{0.0848, constValue(1000)},
		{0.0933, constValue(1250)},
		{0.0339, multipleWorthStatic(getIronIngotWorth, 6)},
		{0.0424, multipleWorthStatic(getIronIngotWorth, 12)},
		{0.0424, multipleWorthStatic(getRedstoneWorth, 36)},
		{0.0169, multipleWorthStatic(getRedstoneWorth, 48)},
		{0.0084, getDiamondWorth},
		{0.0033, multipleWorthStatic(getDiamondWorth, 3)},
		{0.0594, getDiamondPickWorth},
		{0.0339, getIronPickWorth},
		{0.0339, multipleWorthStatic(getCobblestoneStackWorth, 3)},
		{0.0509, multipleWorthStatic(getCobblestoneStackWorth, 4)},
		{0.0679, multipleWorthStatic(getCobblestoneStackWorth, 5)},
		{0.0339, multipleWorthStatic(getGrassBlockWorth, 10)},
		{0.0169, multipleWorthStatic(getSandBlockWorth, 10)},
		{0.0339, multipleWorth(getVoteKeyWorth, 3)},
		{0.0594, multipleWorth(getCommonKeyActualWorth, 2)},
		{0.0339, getRareKeyWorth},
		// skipping some
		{0.0033, getPigSpawnerWorth},
	})
}

func getCommonKeyWorth() float64 {
	return getCommonKeyApparentWorth()
}

func getVoteKeyActualWorth() float64 {
	return randomHelper2([]option{
		{0.0426, constValue(100)},
		{0.0533, constValue(150)},
		{0.0639, constValue(200)},
		{0.0746, constValue(300)},
		{0.0852, constValue(500)},
		{0.0426, multipleWorthStatic(getIronIngotWorth, 3)},
		{0.0319, multipleWorthStatic(getIronIngotWorth, 6)},
		{0.0533, multipleWorthStatic(getRedstoneWorth, 8)},
		{0.0213, multipleWorthStatic(getRedstoneWorth, 16)},
		{0.0042, getDiamondWorth},
		{0.0255, getDiamondPickWorth},
		{0.0746, getIronPickWorth},
		{0.0426, multipleWorthStatic(getCobblestoneStackWorth, 2)},
		{0.0639, multipleWorthStatic(getCobblestoneStackWorth, 3)},
		{0.0852, multipleWorthStatic(getCobblestoneStackWorth, 4)},
		{0.0426, multipleWorthStatic(getGrassBlockWorth, 5)},
		{0.0213, multipleWorthStatic(getSandBlockWorth, 5)},
		{0.0959, multipleWorth(getVoteKeyActualWorth, 2)},
		{0.0426, getCommonKeyWorth},
		{0.0213, getRareKeyWorth},
		// skipping kit
	})
}

func getVoteKeyWorth() float64 {
	return getVoteKeyApparentWorth()
}

func main() {
	num := 1000000
	tmp := float64(multipleWorth(getRareKeyActualWorth, num)()) / float64(num)
	fmt.Println("Rare Key Worth: ", tmp)
	tmp2 := float64(multipleWorth(getCommonKeyActualWorth, num)()) / float64(num)
	fmt.Println("Common Key Worth: ", tmp2)
	tmp3 := float64(multipleWorth(getVoteKeyActualWorth, num)()) / float64(num)
	fmt.Println("Vote Key Worth: ", tmp3)
}
