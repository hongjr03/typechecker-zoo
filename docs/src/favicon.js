// Add social media meta tags for sharing
(function() {
    // Get the current page URL and title
    var url = window.location.href;
    var title = document.title;
    var description = "类型检查器动物园 - 用于学习类型检查器实现的教程";
    var imageUrl = new URL("lean.png", document.baseURI).href;
    
    // Create meta tags for social sharing
    var metaTags = [
        // Open Graph meta tags
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        { property: "og:image", content: imageUrl },
        { property: "og:url", content: url },
        { property: "og:type", content: "website" },
        
        // Twitter Card meta tags
        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:title", content: title },
        { name: "twitter:description", content: description },
        { name: "twitter:image", content: imageUrl },
        
        // General meta tags
        { name: "description", content: description },
        { name: "image", content: imageUrl }
    ];
    
    // Add meta tags to the head
    var head = document.getElementsByTagName('head')[0];
    metaTags.forEach(function(tag) {
        var meta = document.createElement('meta');
        if (tag.property) {
            meta.setAttribute('property', tag.property);
        } else if (tag.name) {
            meta.setAttribute('name', tag.name);
        }
        meta.setAttribute('content', tag.content);
        head.appendChild(meta);
    });
})();
