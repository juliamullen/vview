
function refold(route) {
	const request = new XMLHttpRequest()
	request.open("GET", '/mv/' + route + '/{{ video_path }}', true)
	request.setRequestHeader('Content-Type', 'application/json')
	request.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 204) {
			let link = document.getElementById("next")
			window.location.href = link.href
		}
	}
	request.send()
}

function postTag() {
	const request = new XMLHttpRequest()
	const tag = document.getElementById('tag').value
	document.getElementById('tag').value = ''

	request.open("POST", '/tag', true)
	request.setRequestHeader('Content-Type', 'application/json')
	request.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 204) {
			const newTag = document.createTextNode(' ' + tag)
			document.getElementById('tag-list').appendChild(newTag)
		} 
	}
	request.send(JSON.stringify({
		'tag': tag,
		'video': '{{ video_path }}',
	}))

}

function setSpeed(speed) {
	document.getElementById('topic').playbackRate = speed
}

function rotate(direction) {
	const vid = document.getElementById('topic')
	if (direction == 90) {
		vid.className = 'or'
		return
	}
	if (direction == -90) {
		vid.className = 'ol'
		return
	}
	if (direction == 180) {
		vid.className = 'of'
		return
	}
	vid.className = ''	
}

document.addEventListener('keydown', function(event) {
	let link
	if(event.keyCode == 37) {
		link = document.getElementById("previous")
	}
	else if(event.keyCode == 39) {
		link = document.getElementById("next")
	}
	else if(event.keyCode == 40) {
		link = document.getElementById("rand")
	}

	if (link) {
		window.location.href = link.href
	}
});

let xstart, ystart

let page = document.getElementsByTagName("section")
//const db = document.getElementById("debug")
for (let p of page) {
	p.addEventListener('touchstart', function(e) {
		let t = e.targetTouches.item(0)
		xstart = t.screenX
		ystart = t.screenY
	})
	p.addEventListener('touchmove', function(e) {
		let t = e.targetTouches.item(0)
		xend = t.screenX
		yend = t.screenY
		let xdif = xstart - xend
		let ydif = ystart - yend
		if (xdif > 500) { // swipe left
			window.location.href = document.getElementById("previous").href
		}
		if (xdif < 500) { // swipe right
			window.location.href = document.getElementById("next").href
		}
		if (ydif < 500) {
			window.location.href = document.getElementById("rando").href
		}
	})
}

const topic = document.getElementById("topic");
topic.onloadedmetadata = function() {
	if (this.duration > 15) {
		// between one quarter and three quarters
		this.currentTime = (this.duration / 4) + (Math.random() * this.duration / 2);
	}
	this.playbackRate = .5
}

