# Cumulative sum algorithm (CUSUM) to detect abrupt changes in data.
# https://nbviewer.jupyter.org/github/demotu/BMC/blob/master/notebooks/DetectCUSUM.ipynb
import numpy as np


class CUSUM(object):
    def __init__(self, threshold=1, drift=0):
        self.threshold = threshold
        self.drift = drift

    def detect_cusum(self, x, ending=False):
        """Cumulative sum algorithm (CUSUM) to detect abrupt changes in data.

        Parameters
        ----------
        x : 1D array_like
            data.
        threshold : positive number, optional (default = 1)
            amplitude threshold for the change in the data.
        drift : positive number, optional (default = 0)
            drift term that prevents any change in the absence of change.
        ending : bool, optional (default = False)
            True (1) to estimate when the change ends; False (0) otherwise.
        show : bool, optional (default = True)
            True (1) plots data in matplotlib figure, False (0) don't plot.
        ax : a matplotlib.axes.Axes instance, optional (default = None).

        Returns
        -------
        ta : 1D array_like [indi, indf], int
            alarm time (index of when the change was detected).
        tai : 1D array_like, int
            index of when the change started.
        taf : 1D array_like, int
            index of when the change ended (if `ending` is True).
        amp : 1D array_like, float
            amplitude of changes (if `ending` is True).

        Notes
        -----
        Tuning of the CUSUM algorithm according to Gustafsson (2000)[1]_:
        Start with a very large `threshold`.
        Choose `drift` to one half of the expected change, or adjust `drift` such
        that `g` = 0 more than 50% of the time.
        Then set the `threshold` so the required number of false alarms (this can
        be done automatically) or delay for detection is obtained.
        If faster detection is sought, try to decrease `drift`.
        If fewer false alarms are wanted, try to increase `drift`.
        If there is a subset of the change times that does not make sense,
        try to increase `drift`.

        Note that by default repeated sequential changes, i.e., changes that have
        the same beginning (`tai`) are not deleted because the changes were
        detected by the alarm (`ta`) at different instants. This is how the
        classical CUSUM algorithm operates.

        If you want to delete the repeated sequential changes and keep only the
        beginning of the first sequential change, set the parameter `ending` to
        True. In this case, the index of the ending of the change (`taf`) and the
        amplitude of the change (or of the total amplitude for a repeated
        sequential change) are calculated and only the first change of the repeated
        sequential changes is kept. In this case, it is likely that `ta`, `tai`,
        and `taf` will have less values than when `ending` was set to False.
        """
        x = np.atleast_1d(x).astype('float64')
        gp, gn = np.zeros(x.size), np.zeros(x.size)
        ta, tai, taf = np.array([[], [], []], dtype=int)
        tap, tan = 0, 0
        amp = np.array([])
        # Find changes (online form)
        for i in range(1, x.size):
            s = x[i] - x[i-1]
            gp[i] = gp[i-1] + s - self.drift  # cumulative sum for + change
            gn[i] = gn[i-1] - s - self.drift  # cumulative sum for - change
            if gp[i] < 0:
                gp[i], tap = 0, i
            if gn[i] < 0:
                gn[i], tan = 0, i
            if gp[i] > self.threshold or gn[i] > self.threshold:  # change detected!
                ta = np.append(ta, i)    # alarm index
                tai = np.append(tai, tap if gp[i] > self.threshold else tan)  # start
                gp[i], gn[i] = 0, 0      # reset alarm
        # THE CLASSICAL CUSUM ALGORITHM ENDS HERE

        # Estimation of when the change ends (offline form)
        if tai.size and ending:
            _, tai2, _, _ = self.detect_cusum(x[::-1], ending)
            taf = x.size - tai2[::-1] - 1
            # Eliminate repeated changes, changes that have the same beginning
            tai, ind = np.unique(tai, return_index=True)
            ta = ta[ind]
            # taf = np.unique(taf, return_index=False)  # corect later
            if tai.size != taf.size:
                if tai.size < taf.size:
                    taf = taf[[np.argmax(taf >= i) for i in ta]]
                else:
                    ind = [np.argmax(i >= ta[::-1])-1 for i in taf]
                    ta = ta[ind]
                    tai = tai[ind]
            # Delete intercalated changes (the ending of the change is after
            # the beginning of the next change)
            ind = taf[:-1] - tai[1:] > 0
            if ind.any():
                ta = ta[~np.append(False, ind)]
                tai = tai[~np.append(False, ind)]
                taf = taf[~np.append(ind, False)]
            # Amplitude of changes
            amp = x[taf] - x[tai]
        return ta, tai, taf, amp
