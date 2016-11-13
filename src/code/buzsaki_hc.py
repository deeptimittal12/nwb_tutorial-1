###################################
###################################
########### TODO
###################################
###################################

def remove_slow_sections(X, xFs, pos, posFs, pctCutoff):
	'''
	Remove sections from X where the rat's velocity is less than pctCutoff * maxSpeed.
	'''
	pos = np.copy(pos[:, 0:2])

	# Replace -1s with -1e6. This will make it easy to remove these sections later.
	for i in range(pos.shape[0]):
		if ( pos[i][0] == -1 or pos[i][1] == -1 ):
		# if ( math.isnan(pos[i][0]) or math.isnan(pos[i][1]) ):
			pos[i] = -1e6

	# Calculate the velocity.
	vx = np.diff(pos[:,0])
	vy = np.diff(pos[:,1])	

	# Make places where the position is undefined have zero velocity.
	for i in range(vx.shape[0]):
		if(np.abs(vx[i]) > 1e5):
			vx[i] = 0
			vy[i] = 0

	# Calculate the speed.
	speed = np.sqrt(vx**2 + vy**2)
	maxSpeed = np.max(speed)

	# Create an interpolated speed array sampled at xFs
	tPos = np.arange(0, speed.shape[0]) / posFs
	tX = np.arange(0, X.shape[1]) / xFs

	outsideInterpolationRange = np.where(tX > tPos[-1])[0]
	tX = np.delete(tX, outsideInterpolationRange)

	interpolateSpeed = interpolate.interp1d(tPos, speed)
	speed = interpolateSpeed(tX)

	# Calculate indices where the rat is moving too slow.
	tooSlowIndices = np.where(speed < pctCutoff * maxSpeed)[0]

	# Remove sections where the rat is moving too slow or outside the interpolation range.
	newX = np.delete(X, np.concatenate((tooSlowIndices, outsideInterpolationRange)), axis=1)
	newTX = np.delete(tX, tooSlowIndices)
	
	return newX, newTX

