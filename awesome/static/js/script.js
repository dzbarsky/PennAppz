$(document).ready(function(){

$(".response,#eval,#buttons,#load,#check_fill,#x_fill").hide();


var allResponses = [];

var current_code;

//WHEN USER HITS SUBMIT
$(document).on('click','#submit',function(){

	$("#load").show();

  var code = $('input[name=keyword]').val();
    $('#check-disabled,#X-disabled,#new-disabled').fadeTo('slow',1,function() {
	var cl = $(this).attr('class').replace( '-disabled','');
	$(this).removeAttr('class').attr('class',cl);
	var id = $(this).attr('id').replace('-disabled','');
	$(this).removeAttr('id').attr('id',id);
     });
  $.post('course_search/',{coursecode: code}, function(response) {
      allResponses = $.parseJSON(response);
      processData();
  });
  return false;
});

var courseHtml = $('<div id="course"></div>');
var currentCourseTitle;

var processData = function() {
  console.log(allResponses);
  var this_course = allResponses ? allResponses.shift() : null;
  $('#this_course').text(this_course['id']);
  $('#viewing-random').hide();
  $('#course_title').text(this_course['title']).closest('#viewing').show();
  var course = allResponses ? allResponses.shift() : null;
      
	$('#searchbar').animate({
	     top: '20px',
   	}, 300, "linear");
	$("#buttons,#eval,.response").fadeIn();
	$(".response").flippy({
		verso: courseHtml,
		duration:"500",
		color_target: "#E0EEEE",
		//color_target:'#CAEEFD',
		onFinish: updateCourse(course)
	});
	
	$("#load").hide();
	return false;
};

var updateCourse = function(course) {
	$("#check_fill").hide();
	$("#x_fill").hide();
    if (course) {
        current_code = course["coursecodes"][0];
        currentCourseTitle = course["title"];
        courseHtml.empty();
        $(document.createElement('div')).attr('id','title').text(course["title"]).appendTo(courseHtml);
        $(document.createElement('div')).attr('id','codes').text(course["coursecodes"].join(", ")).appendTo(courseHtml);
        var d = course["description"];
        var len = d.toString().length;
        if (len>1300) {
        	a = d.substr(0, 1100) + '...';
        }
        else {a=d;}
        $(document.createElement('div')).attr('id','c_descrip').text(a).appendTo(courseHtml);

        if (course["courseQuality"] != -1 &&
            course["instructorQuality"] != -1 &&
            course["difficulty"] != -1) {
            $(document.createElement('div')).attr('id','diff').text("Difficulty: "+course["difficulty"]+" | "+"Course Quality: "+course["courseQuality"]+" | "+"Instructor Quality: "+course["instructorQuality"]).appendTo($(document.createElement('div')).attr('id','ratings').appendTo(courseHtml));
        }
    } else {
            courseHtml.empty();
            $(document.createElement('div')).attr('id','title').text("Sorry, we could not find this course in our database.  Our database is still expanding.  This is a work in progress!").appendTo(courseHtml);
    }
}

	$("#submit").mousedown(function(){
	$(this).css('background-color','#ACD0FD');
});
$("#submit").mouseup(function(){
	$(this).css('background-color','#5c80cb');
});

$(document).on('mousedown','#random,#new,#save',function(){
	// $(this).fadeOut();
	$(this).animate({
		opacity:0.7,
	},100);
});
$(document).on('mouseup','#random,#new,#save',function(){
	$(this).animate({
		opacity:1,
	},100);
});

$(document).on('click','#new',function(){
	$(".response").flippy({
		verso:courseHtml,
		duration:"500",
		color_target: "#E0EEEE",
    onStart: function() {
        var course;
        do {
          course = allResponses.shift();
        } while (course && course["title"] == currentCourseTitle);
        if (course) {
          updateCourse(course);
        }
    }
	});
	return false;
});

$(document).on('click','#random',function(){
	$('input[name=keyword]').val('');
	$('#viewing').hide();
	$('#viewing-random').show();
	$('#check,#X,#new').fadeTo('slow',0.1,function() {
		var cl = $(this).attr('class') + '-disabled';
		$(this).removeAttr('class').attr('class',cl);
		var id = $(this).attr('id') + '-disabled';
		$(this).removeAttr('id').attr('id',id);
	});
	$.post('random_course/',function(response) {
		$(".response").flippy({
			verso: courseHtml,
			duration:"500",
			color_target: "#E0EEEE",
			//color_target:'#CAEEFD',
			onFinish: updateCourse($.parseJSON(response)[0]),
		});
	});
	return false;
});

$(document).on('click',"#check",function() {
	$.post('user_feedback/',
		{ searched_course: $('input[name=keyword]').val(),
		  courseid2: $('#this_course').text(),
		  feedback: 'thumbs_up' });
	$("#check_fill").show();
	$("#x_fill").hide();
});

$(document).on('click',"#X",function() {
	$.post('user_feedback/',
		{ searched_course: $('input[name=keyword]').val(),
		  courseid2: $('#this_course').text(),
		  feedback: 'thumbs_down' });
	$("#check_fill").hide();
	$("#x_fill").show();
});

$(document).on('click','#save',function(){
	$(document.createElement('div')).attr('id', 's1').attr('style','cursor:pointer').height('40px').width($("#sidebar").width()).text(current_code).css({ 'font-size':'0.8em','background-color': '#E0EEEE', padding:'8px', position: 'relative', left: 0, top: 0, margin: "5px", textAlign: "left", 'line-height':'40px', color: "#000", 'border-radius':'10px' }).prependTo($('#sidebar')).hide();
	$(document.createElement('div')).attr('class','close').text('x').css({position:'absolute',right:10, 'text-align':'right', 'line-height':'40px', width:'20px',height:'40px',color:'#fff'}).prependTo($('#s1'));
	$("#s1").slideDown();
});





$(document).on('click','.close',function() {
	$(this).parent().slideUp(function complete(){
		$(this).remove();
	});
});

$('#check').hover(function(){
	$("#descrip").text("I like this recommendation!");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$('#X').hover(function(){
	$("#descrip").text("I hate this recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

$('#new').hover(function(){
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
