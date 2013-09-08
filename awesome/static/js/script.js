$(document).ready(function(){

$(".response,#eval,#buttons").hide();


//WHEN USER HITS SUBMIT
$("#searchbar").submit(function(){
//moves searchbar up
	$('#searchbar').animate({
	     top: '20px',
   	}, 300, "linear");
//buttons, response box appears
	$("#buttons,#eval,.response").fadeIn();
//flips response panel
	$(".response").flippy({
		//verso: $("input:first").val(),
		verso: $('<div id="oli"></div>'),
		duration:"500",
		color_target: "#E0EEEE",
		//color_target:'#CAEEFD',
		onFinish: function(){
			//insert text in these
			$(document.createElement('div')).attr('id','c_descrip').text("Learn how to program").prependTo("#oli");
			$(document.createElement('div')).attr('id','title').text("Intro to Programming").prependTo("#oli");
			$(document.createElement('div')).attr('id','code').text("CIS 110").prependTo("#oli");
			$(document.createElement('div')).attr('id','prof').text().prependTo("#oli");
		}
	});

	
	return false;
});

$("#submit").mousedown(function(){
	$(this).css('background-color','#5c80cb');
});
$("#submit").mouseup(function(){
	$(this).css('background-color','#ACD0FD');
});

$(".icon").mousedown(function(){
	// $(this).fadeOut();
	$(this).animate({
		opacity:0.7,
	},100);
});
$(".icon").mouseup(function(){
	$(this).animate({
		opacity:1,
	},100);
});

$("#new").click(function(){
	$(".response").flippy({
		verso:"something new",
		duration:"500",
		color_target: "#E0EEEE"
	});
	return false;
});

$("#random").click(function(){
	$(".response").flippy({
		verso:"random class!",
		duration:"500",
		color_target: "#E0EEEE"
	});
	return false;
});

$("#save").click(function(){
	$(document.createElement('div')).attr('id', 's1').attr('style','cursor:pointer').height('40px').width($("#sidebar").width()).text($("#code").text()).css({ 'font-size':'0.8em','background-color': '#E0EEEE', padding:'8px', position: 'relative', left: 0, top: 0, margin: "5px", textAlign: "left", 'line-height':'40px', color: "#000", 'border-radius':'10px' }).prependTo($('#sidebar')).hide();
	$(document.createElement('div')).attr('class','close').text('x').css({position:'absolute',right:10, 'text-align':'right', 'line-height':'40px', width:'20px',height:'40px',color:'#fff'}).prependTo($('#s1'));
	$("#s1").slideDown();
});



$(document).on('click','.close',function() {
	$(this).parent().slideUp(function complete(){
		$(this).remove();
	});
});

$("#check").hover(function(){
	$("#descrip").text("I like this recommendation!");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$("#X").hover(function(){
	$("#descrip").text("I hate this recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$("#new").hover(function(){
	$("#descrip").text("I'd like a new recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$("#random").hover(function(){
	$("#descrip").text("Generate a random course for me!");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$("#save").hover(function(){
	$("#descrip").text("I'd like to save this recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

}); //document ready