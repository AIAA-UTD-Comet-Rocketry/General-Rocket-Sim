from datetime import timedelta
import numpy as np

class IterationManager():
    def __init__(self, startDay):
        self.varyingPossibilitiesName = ["Fin Position", "Day", "Hour"]
        self.varyingPossibilitiesKeyMapping = ["fin_position", "day", "hour"]
        # put the start end range (inclusive), then the # of elements you want in between them
        self.varyingRanges = [
            [2.67, 2.92, 11],
            [0, 1, 2],
            [5, 6, 2]
        ]

        self.CreateInitialIteratorValues(startDay)

        self.iterative_variables = []

        self.readable_names = []
        self.true_names = []
        self.true_ranges = []
        self.true_current_indices = []

        self.SetupChosenIteratorValues()

    def CreateInitialIteratorValues(self, startDay):
        for i in range(len(self.varyingRanges)):
            self.varyingRanges[i] = np.linspace(*self.varyingRanges[i]).tolist()
            if self.varyingPossibilitiesKeyMapping[i] == "day":
                for j in range(len(self.varyingRanges[i])):
                    trueDate = startDay + timedelta(days = j)
                    self.varyingRanges[i][j] = [trueDate.year, trueDate.month, trueDate.day]

    def SetupChosenIteratorValues(self):
        for i in range(len(self.iterative_variables)):
            try:
                currentStr = self.iterative_variables[i]
                trueIndex = self.varyingPossibilitiesName.index(currentStr)
                self.readable_names.append(self.varyingPossibilitiesName[trueIndex])
                self.true_names.append(self.varyingPossibilitiesKeyMapping[trueIndex])
                self.true_ranges.append(self.varyingRanges[trueIndex])
                self.true_current_indices.append(0)
            except ValueError:
                print("element not found! abort immedietly!")
                raise SystemExit

    def UpdateIterativeVariables(self, Parameters):
        for i in range(len(self.true_names)):
            trueParamString = self.true_names[i]
            trueIndexInRange = self.true_current_indices[i]
            trueNextVal = self.true_ranges[i][trueIndexInRange]

            Parameters[trueParamString] = trueNextVal

    # note: returns whether or not we're fully done
    def UpdateIteratorIndices(self):
        for i in range(len(self.true_names) - 1, -1, -1):
            if(self.true_current_indices[i] < len(self.true_ranges[i]) - 1):
                self.true_current_indices[i] += 1
                return False
            else:
                self.true_current_indices[i] = 0

        return True

    def MoveToNextIteration(self, Parameters):
        everythingFinished = self.UpdateIteratorIndices()
        if everythingFinished:
            return True

        self.UpdateIterativeVariables(Parameters)
        return False