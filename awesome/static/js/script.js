$(document).ready(function(){

//$("#response").hide();
	
$("#eval,#buttons").hide();

$("#searchbar").submit(function(){
	//$('#searchbar').css('color','#ffffff');
	// $('#searchbar').animate({
	//     top: '20px',
 //  	}, 400, "linear", function() {});
	
	$("#buttons,#eval").fadeIn();
	$(".response").flippy({
		verso: $("input:first").val(),
		duration:"500",
		color_target: "#E0EEEE"
	});
	return false;
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

$("#save").click(function(){
	$(document.createElement('div')).attr('id', 's1').attr('style','cursor:pointer').height('40px').width($("#sidebar").width()).text($(".response").text()).css({ 'font-size':'0.8em','background-color': '#E0EEEE', padding:'8px', position: 'relative', left: 0, top: 0, margin: "5px", textAlign: "left", 'line-height':'40px', color: "#000", 'border-radius':'10px' }).prependTo($('#sidebar')).hide();
	$(document.createElement('div')).attr('class','close').text('x').css({position:'absolute',right:10, 'text-align':'right', 'line-height':'40px', width:'20px',height:'40px',color:'#fff'}).prependTo($('#s1'));
	$("#s1").slideDown();
});

$("#new").click(function(){
	$(".response").flippy({
		verso:"something new",
		duration:"500",
		color_target: "#E0EEEE"
	});
	return false;
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

$("#save").hover(function(){
	$("#descrip").text("I'd like to save this recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

}); //document ready