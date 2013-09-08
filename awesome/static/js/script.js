$(document).ready(function(){

$(".response,#eval,#buttons,#load").hide();


var allResponses = [];

var current_code;

//WHEN USER HITS SUBMIT
$("#searchbar").submit(function(){

	$("#load").show();

  var code = $('input[name=keyword]').val();
  $.post('course_search/',{coursecode: code}, function(response) {
      allResponses = $.parseJSON(response);
      processData();
  });
  return false;
});

var courseHtml = $('<div id="course"></div>');
var currentCourseTitle;

var processData = function() {
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
    if (course) {
        var current_code = course["coursecodes"][0];
        currentCourseTitle = course["title"];
        courseHtml.empty();
        $('#this_course').text(course['id']);
        $(document.createElement('div')).attr('id','title').text(course["title"]).appendTo(courseHtml);
        $(document.createElement('div')).attr('id','codes').text(course["coursecodes"].join(", ")).appendTo(courseHtml);
        $(document.createElement('div')).attr('id','c_descrip').text(course["description"]).appendTo(courseHtml);

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

$("#random").click(function(){
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

$("#save").click(function(){
	$(document.createElement('div')).attr('id', 's1').attr('style','cursor:pointer').height('40px').width($("#sidebar").width()).text(current_code).css({ 'font-size':'0.8em','background-color': '#E0EEEE', padding:'8px', position: 'relative', left: 0, top: 0, margin: "5px", textAlign: "left", 'line-height':'40px', color: "#000", 'border-radius':'10px' }).prependTo($('#sidebar')).hide();
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

$(document).on('click',"#check",function() {
	$.post('user_feedback/',
		{ searched_course: $('input[name=keyword]').val(),
		  courseid2: $('#this_course').text(),
		  feedback: 'thumbs_up' });
});

$(document).on('click',"#X",function() {
	$.post('user_feedback/',
		{ searched_course: $('input[name=keyword]').val(),
		  courseid2: $('#this_course').text(),
		  feedback: 'thumbs_down' });
});

$("#save").hover(function(){
	$("#descrip").text("I'd like to save this recommendation.");
	$("#descrip").fadeIn(100);
},function(){
	$("#descrip").fadeOut(100);
});

}); //document ready
