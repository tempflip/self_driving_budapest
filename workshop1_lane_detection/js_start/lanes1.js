var cv = require('opencv');
IMG_PATH_1 = '../images/img1.png';
OUT_FILE = 'out1.png';


cv.readImage(IMG_PATH_1, function(err, image){
	//img.convertGrayscale();
	img = image.copy()
	img.canny(5, 300);

	var lines = img.houghLinesP();

	lines.forEach(function(line) {
		var x1 = line[0];
		var y1 = line[1];
		var x2 = line[2];
		var y2 = line[3];

		image.line([x1, y1], [x2, y2], [100, 10, 77], 4);
	});

	image.save(OUT_FILE);

	console.log('we are good, check ', OUT_FILE);
});
