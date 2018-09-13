TrendTree idea:

Detection of new trend is done by using a given indicator, and determining a slope sign change from negative to positive, or positive to negative

1) Basic premise is to keep track of market cycles beginning with smallest detectable trend, designate this point as trend.start_price, trend.high_price, trend.low_price. If trend is moving downward, designate trend.direction = -1, if moving up trend.direction = 1.

2) if trend.direction == 1 and price passes below trend.start_price, or slope sign change from positive to negative, set trend.end_price = price
else if trend.direction == -1 and price passes above trend.end_price, or slope sign change from negative to positive, set trend.end_price = price

3) Set this trend as the "trend tree" root if no root exists and create new trend as in step 1

4) repeating step 2, we then determine if the newly ended trend is a subset of the root, or if the root is a subset of the newly ended trend.

5) if the trend is a subset of root: add the new trend to the root trend's list of children
   otherwise if the root is a subset of the new trend, set the new trend as root, and add the old root to the new roots list of children

6) Continue to build tree in this fashion. Every time new trend is being added to tree, check root and all children to see if trend should be a child of one of the children.

7) Also when being added, if the new trend is not a subset of root, and extends below or above root but also part of it is contained in root, and if the direction value is
   the same as root direction, then merge this trend with root. If the new trend is a subset of root, and is not a subset of one of the children, but does extend the child / also
   partially contained in the child and has same direction of child, then merge with that child

8) If a trend forms such that the root (or it's children) become a subset of that trend but with opposite direction sign, then remove root (or it's children) and all subsets of that trend,
   and replace with the trend with opposite direction sign in its place
   
   
Using this tree, we should be able to determine both the major trend (from root), and minor trend (from one of root's children)
