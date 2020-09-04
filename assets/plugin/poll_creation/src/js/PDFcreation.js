// PDF Poll Creation

var toPx = 96 / 72;
var docWidth = 1504;
var docHeight = 1129;
// var docWidth = 1224;
// var docHeight = 792;

/* Defining widths and heights for result pdf of components */
var mm10 = 37.8; //px; mm:10;
var left_x = mm10; //px; mm:10;
var right_x = 1000; //px; mm:180;
var logoHeight = mm10*2; 
var leftHeight = docHeight - logoHeight - mm10;
var leftWidth = right_x - mm10; 
var qrCodeHeight = docHeight - mm10*5;
var qrCodeWidth = docWidth - right_x - mm10; 
var resultHeight = docHeight - mm10*0;
var resultWidth = docWidth - right_x - mm10*2; 

/**
 * Create the general pdf 
 */
function generatePDFLayout(){
    var properties = {title: 'SourceCloze', subject:'PollCreation', author: ctCreator};
	    // keywords: 'generated, javascript, web 2.0, ajax',
	    // creator: 'MEEE'
    var pdf = new jsPDF('l', 'px', [docWidth*toPx, docHeight*toPx]);
	pdf.setProperties(properties);
	pdf.setFontSize(26);
	return pdf
}


/**
 * Build pdf slides based on poll resolution
 */
async function buildResultPages(pdf, sel){
	console.log(document.querySelector(sel))
	await html2canvas(document.querySelector(sel), {scrollY: -window.scrollY})
		.then(async canvas => {
			console.log(canvas)
			try {
	            contentH = $(sel).height();
	            var img = canvas.toDataURL("image/png", 1.0);
	            $w = $actw = canvas.width;
	            $h = $acth = canvas.height;
	            var width = $maxw = resultWidth;
	            var height = $maxh = resultHeight;
	            if (!$maxw) $maxw = width;
	            if (!$maxh) $maxh = height;
	            if ($w > $maxw) {
	                $w = $maxw;
	                $h = Math.round($acth / $actw * $maxw);
	            }
	            pdf.addImage(img, 'PNG', right_x, mm10*0, $w, $h);
	            await buildLeftSite(pdf)
	            $count = Math.ceil($h / $maxh) - 1;
	            for (var i = 1; i <= $count; i++) {
	                position = - $maxh * i;
	                pdf.addPage();
	                pdf.addImage(img, 'PNG', right_x, position, $w, $h);
	            	await buildLeftSite(pdf)
	            }
	        } catch (e) {
	            alert("Error description: " + e.message);
	        }
	        return
        })
	return
}


/**
 * Build the left site of pdf (equal for access and resolution)
 */
async function buildLeftSite(pdf){
	console.log("BUILD LEFT SITE")
	console.log("BUILD logo")
	await addCanvas(pdf, 'logo', left_x,  mm10*0, getScaleFactorLogo);
	await addCanvas(pdf, 'code-view', left_x, mm10*5, getScaleFactorLeft);
}

/**
 * Build right site from access view. Contains url, pollId and qrcode
 */
async function buildRightSiteQrCode(pdf){
	pdf.setFontSize(22);
	pdf.textWithLink(url, right_x, mm10*3, {url: url+'/views/poll/'+ctId});
	pdf.setFontType("bold");
	pdf.setFontSize(26);
	pdf.setTextColor("#3068c1");
	pdf.text(right_x, mm10*4, "Umfrage-ID: "+ctId);
	pdf.setFontType("normal");
	pdf.setTextColor("#000000");
	await addCanvas(pdf, 'qrcode', right_x, mm10*5, getScaleFactorQrCode);
}
// async function buildRightSiteResult(pdf){
// 	await addCanvas(pdf, "#answerview", right_x,  mm10*0, getScaleFactorResult);
// }


/**
 * Create a canvas from an html element given with a 'selector' and adds it to the pdf on position x,y 
 * optionally it is possible to give a scalefunction 
 */
async function addCanvas(pdf, sel, x, y, scalef){
	console.log(sel +":");
	var newSize = [$("#"+sel).width(), $("#"+sel).height()]
	if (scalef)
		newSize = scalef($("#"+sel).width(), $("#"+sel).height());
	return await html2canvas(document.getElementById(sel), {scrollY: -window.scrollY, scale: 3})
		.then(canvas => {
		pdf.addImage(
			canvas.toDataURL('image/png', 1.0), 'JPG', 
			x, y, 
			newSize[0], newSize[1] // width , height
			);
		return
	}); 
}

/**
 * Scales given src (containing src.width and src.height) to a destination
 * Returns an array like [newWidth, newHeight]
 */
function scale(src, dst){
    var scale = Math.min( dst.width/src.width, dst.height/src.height);
    var res = [src.width * scale, src.height * scale];
	console.log("\tsrc: ("+ src.width + ", "+ src.height +")");
	console.log("\tdst: ("+ dst.width + ", "+ dst.height +")");
	console.log("\tres: ("+ res[0] + ", "+ res[1] +")");
	return res;
}

/**
 * Scale functino for the source cloze logo
 */
function getScaleFactorLogo(w1,h1){
	return scale({width:w1, height:h1}, {width:docWidth, height:logoHeight});
}

/**
 * Scale functino for the left site (source code/ cloze test)
 */
function getScaleFactorLeft(w1,h1){
	return scale({width:w1, height:h1}, {width:leftWidth, height:leftHeight});
}

/**
 * Scale functino for the qr code
 */
function getScaleFactorQrCode(w1,h1){
	return scale({width:w1, height:h1}, {width:qrCodeWidth, height:qrCodeHeight});
}

/**
 * Scale functino for the answe of source cloze logo
 */
// function getScaleFactorResult(w1,h1){
// 	return scale({width:w1, height:h1}, {width:resultWidth, height:resultHeight});
// }

