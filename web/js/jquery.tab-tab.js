;(function($) {
	
	$.fn.tabTab = function(options) {
		
		
		/*
		Variables
		---------- */
		
		var $this = $(this),
			ul = $this.find('nav ul'),
			a = ul.find('li a'),
			section = $this.find('section'),
			currentTab,
			currentSection,
			settings = $.extend({
				index: 0,
				saveState: true,
			},options);
			
		
		/*
		Initialization
		---------- */	
		
		// load state
		if(settings.saveState === true && localStorage.getItem('index.tabtab')) setCurrent(localStorage.getItem('index.tabtab'));
		// default index
		else setCurrent(settings.index);
		
		
		/*
		Private methods
		---------- */
		
		function setCurrent(index) {
			
			if(index >= a.length) index = a.length - 1;
			else if(index < 0) index = 0;
			
			
			$this.find('.current').removeClass('current');
			
			currentTab = a.eq(index).addClass('current');
			currentSection = section.eq(index).addClass('current');
			
			
			// save state
			if(settings.saveState === true) localStorage.setItem('index.tabtab',index);
		}
		
		
		/*
		Events
		---------- */
		
		ul
		.delegate('li a','mouseover focus',function() {
			
			currentTab.removeClass('current');
		})
		.delegate('li a','mouseout blur',function() {
			
			currentTab.addClass('current');
		})
		.delegate('li a','click',function() {
			
			var $this = $(this);
			
			setCurrent($(this).index('li a'));
			
			// manually trigger blur for Firefox, Opera and maybe others
			$this.trigger('blur');
			
			return false;
		});
		
		
		
		return this;
	}
	
})(jQuery);