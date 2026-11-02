from matplotlib.patches import Ellipse
from imageio import imread
from scipy.stats import norm
from matplotlib import pyplot as plt
import numpy as np

def CreateDistributionPlot(resultsFile, dispersonResultArray, name, generatedFilesLocation, lowerProbBound, upperProbBound, maxDecimals, percentConfidence, hypothesis, unit, makeGraph, filename):
    mean = np.mean(dispersonResultArray)
    deviation = np.std(dispersonResultArray)
    unitString = ""
    if(unit == "meters"):
        unitString = "m"
    print(
        f'{name} -         Mean Value: {mean:0.3f} ' + unitString
    )
    resultsFile.write(f'{name} -         Mean Value: {mean:0.3f} ' + unitString + "\n")
    print(
        f'{name} - Standard Deviation: {deviation:0.3f} m' + unitString
    )
    resultsFile.write(f'{name} - Standard Deviation: {deviation:0.3f} m' + unitString + "\n")
    if(makeGraph):

        print(f"Arr: {dispersonResultArray}")
        minimum = np.min(dispersonResultArray)
        maximum = np.max(dispersonResultArray)
        theBins = list()

        #using scott's rule to find the number of bins
        binWidth = 3.5 * deviation / np.power(len(dispersonResultArray), 1/3)
        numBins = int(np.round((maximum-minimum)/binWidth))

        changeInZ = (maximum - minimum) / numBins
        #test add
        zIterator = minimum
        for iterator in range(numBins):
            theBins.append(zIterator)
            zIterator += changeInZ
        finalValue = np.ceil(zIterator * np.power(10, maxDecimals)) / np.power(10, maxDecimals)
        theBins.append(finalValue)
        plt.figure()
        plt.xlim(minimum, maximum)
        minTextSize = 8
        maxTickCount = 50
        xTickBins = theBins
        if(numBins > maxTickCount):
            xTickBins = list()
            changeInZ = (maximum - minimum) / 50.0
            zIterator = minimum
            for iterator in range(50):
                xTickBins.append(zIterator)
                zIterator += changeInZ
        binListToString = list()
        for currentBin in xTickBins:
            binListToString.append(str(round(currentBin, maxDecimals)))
        plt.xticks(ticks = xTickBins, labels = binListToString, rotation = 75, fontsize = minTextSize)
        plt.hist(dispersonResultArray, bins=theBins)
        plt.title(name)
        plt.xlabel(name)
        plt.ylabel("Number of Occurences")

        plt.axvline(mean, color='k', linestyle='solid', linewidth=4)
        plt.axvline(mean - deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean - 2*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean - 3*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + 2*deviation, color='g', linestyle='solid', linewidth=3)
        plt.axvline(mean + 3*deviation, color='g', linestyle='solid', linewidth=3)
        plt.savefig(generatedFilesLocation + str(filename) + "Graph.png", bbox_inches="tight", pad_inches=0)
        plt.show()
    lowerZ = (lowerProbBound - mean)/deviation
    upperZ = (upperProbBound - mean)/deviation
    probabilityInRange = norm.cdf(upperZ) - norm.cdf(lowerZ)
    print("PROBABILITY THE " + name +  " IS IN BETWEEN " + str(round(lowerProbBound, 4)) + " AND " + str(round(upperProbBound, 4)) + " IS: " + str(round(probabilityInRange * 100, 2)) + "%")
    resultsFile.write("PROBABILITY THE " + name +  " IS IN BETWEEN " + str(round(lowerProbBound, 4)) + " AND " + str(round(upperProbBound, 4)) + " IS: " + str(round(probabilityInRange * 100, 2)) + "%\n")
    if(percentConfidence != 100):
        aVal = (100 - percentConfidence)/100
        newZ = np.abs(norm.ppf(aVal/2))
        lowerBoundOfInterval = mean - newZ * deviation/np.sqrt(len(dispersonResultArray))
        upperBoundOfInterval = mean + newZ * deviation/np.sqrt(len(dispersonResultArray))
        print("There is a " + str(percentConfidence) + f"% chance that the mean of the " + name + 
              " falls within THIS RANGE: " + str(lowerBoundOfInterval) + ", " + str(upperBoundOfInterval))
        resultsFile.write("There is a " + str(percentConfidence) + f"% chance that the mean of the " + name + 
              " falls within THIS RANGE: " + str(lowerBoundOfInterval) + ", " + str(upperBoundOfInterval) + "\n")
        if(hypothesis != None):
            criticalValue = norm.ppf(aVal / 2)
            testStatistic = (mean - hypothesis) * np.sqrt(len(dispersonResultArray))/deviation
            print("\nWe have the hypothesis that our mean is greater than or equal to " + str(hypothesis) + ". With our critical percent, our critical value is " +
                str(criticalValue) + ". Then, our test statistic is " + str(testStatistic))
            resultsFile.write("\nWe have the hypothesis that our mean is greater than or equal to " + str(hypothesis) + ". With our critical percent, our critical value is " +
                str(criticalValue) + ". Then, our test statistic is " + str(testStatistic) + "\n")
            if(testStatistic < criticalValue):
                print("Since our test statistic is more extreme than our critical value, we can reject the null hypothesis that the mean is " + str(hypothesis) + ".\n")
                resultsFile.write("Since our test statistic is more extreme than our critical value, we can reject the null hypothesis that the mean is " + str(hypothesis) + ".\n\n")
            else:
                print("Since our test statistic is less extreme than our critical value, we can NOT reject the null hypothesis that the mean is " + str(hypothesis) + ".\n")
                resultsFile.write("Since our test statistic is less extreme than our critical value, we can NOT reject the null hypothesis that the mean is " + str(hypothesis) + ".\n\n")

def PrintLandingPlots(resultsFile, plotFilename, imgPath, impactXVals, impactYVals, apogee_x, apogee_y):
    img = imread("../InputFiles/background.jpg")
    # Retrieve dispersion data por apogee and impact XY position
    impact_x = np.array(impactXVals)
    impact_y = np.array(impactYVals)

    print(f"Simulated Landing Position x = {np.mean(impact_x)}, y = {np.mean(impact_y)}")
    resultsFile.write(f"Simulated Landing Position x = {np.mean(impact_x)}, y = {np.mean(impact_y)}\n")
    # # Define function to calculate eigen values
    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:, order]


    # Create plot figure
    plt.figure(num=None, figsize=(8, 6), dpi=150, facecolor="w", edgecolor="k")
    ax = plt.subplot(111)

    # Calculate error ellipses for impact
    impactCov = np.cov(impact_x, impact_y)
    impactVals, impactVecs = eigsorted(impactCov)
    impactTheta = np.degrees(np.arctan2(*impactVecs[:, 0][::-1]))
    impactW, impactH = 2 * np.sqrt(impactVals)

    # Draw error ellipses for impact
    impact_ellipses = []
    for j in [1, 2, 3]:
        impactEll = Ellipse(
            xy=(np.mean(impact_x), np.mean(impact_y)),
            width=impactW * j,
            height=impactH * j,
            angle=impactTheta,
            color="black",
        )
        impactEll.set_facecolor((0, 0, 1, 0.2))
        impact_ellipses.append(impactEll)
        ax.add_artist(impactEll)

    # Calculate error ellipses for apogee
    apogeeCov = np.cov(apogee_x, apogee_y)
    apogeeVals, apogeeVecs = eigsorted(apogeeCov)
    apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:, 0][::-1]))
    apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

    # Draw error ellipses for apogee
    for j in [1, 2, 3]:
        apogeeEll = Ellipse(
            xy=(np.mean(apogee_x), np.mean(apogee_y)),
            width=apogeeW * j,
            height=apogeeH * j,
            angle=apogeeTheta,
            color="black",
        )
        apogeeEll.set_facecolor((0, 1, 0, 0.2))
        ax.add_artist(apogeeEll)

    # Draw launch point
    plt.scatter(0, 0, s=30, marker="*", color="black", label="Launch Point")
    # Draw apogee points
    plt.scatter(
        apogee_x, apogee_y, s=5, marker="^", color="green", label="Simulated Apogee"
    )
    # Draw impact points
    plt.scatter(
        impact_x, impact_y, s=5, marker="v", color="blue", label="Simulated Landing Point"
    )

    plt.legend()

    # Add title and labels to plot
    ax.set_title(
        "1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses: Apogee and Lading Points"
    )
    ax.set_ylabel("North (m)")
    ax.set_xlabel("East (m)")

    # Add background image to plot
    # You can translate the basemap by changing dx and dy (in meters)
    dx = 0
    dy = 0
    plt.imshow(img, zorder=0, extent=[-1000 - dx, 1000 - dx, -1000 - dy, 1000 - dy])

    plt.axhline(0, color="black", linewidth=0.5)
    plt.axvline(0, color="black", linewidth=0.5)
    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)

    # Save plot and show result
    plt.savefig("../Output/" + str(plotFilename) + ".pdf", bbox_inches="tight", pad_inches=0)
    plt.savefig("../Output/" + str(plotFilename) + ".svg", bbox_inches="tight", pad_inches=0)
    plt.show()

def ShowTrendlineData(graphData, varName, fileLoc):
    varyingVals = []
    apogeeAtVal = []

    prevVal = None

    for data in graphData:
        if(data[0] != prevVal):
            varyingVals.append(data[0])
            prevVal = data[0]
            apogeeAtVal.append([data[1]])
        else:
            apogeeAtVal[-1].append(data[1])

    print(varyingVals)
    print(apogeeAtVal)

    apogeeAtVal = [np.mean(elem) for elem in apogeeAtVal]

    

    plt.scatter(varyingVals, apogeeAtVal)

    plt.title(f"Apogee at different {varName}s")
    plt.xlabel(varName)
    plt.ylabel("Apogee")
    plt.axhline(3048, color='k', linestyle='solid', linewidth=4)
    plt.text(9.75, 3048, f'Desired Apogee', va='bottom', ha='left', color='red')
    
    #creating the trendline with the given x and y values
    trendline = np.polyfit(varyingVals, apogeeAtVal, 1)
    trendline = np.poly1d(trendline)
    # obtaining the y values from the trendline
    y_vals = trendline(varyingVals)

    # R^2 calculation
    residuals = apogeeAtVal - y_vals
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((apogeeAtVal - np.mean(apogeeAtVal))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # plotting the trendline
    plt.plot(varyingVals, y_vals, "r", label="Trendline (R² = " + str(round(r_squared, 3)) + ")")
    plt.legend()

    plt.savefig(fileLoc + f"FinalSimTable{varName}.png", bbox_inches="tight", pad_inches=0)
    plt.show()
