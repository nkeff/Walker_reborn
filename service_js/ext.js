var attributes = {
    'element': 'data-tryxpath-element',
    'context': 'data-tryxpath-context',
    'focused': 'data-tryxpath-focused',
    'focusedAncestor': 'data-tryxpath-focused-ancestor',
    'frame': 'data-tryxpath-frame',
    'frameAncestor': 'data-tryxpath-frame-ancestor'
};

var cssId = 'myCss';  // you could encode the css path itself to generate id..
var head  = document.getElementsByTagName('head')[0];
var link  = document.createElement('link');
link.id   = cssId;
link.rel  = 'stylesheet';
link.type = 'text/css';
link.href = 'http://aidbox.ru/xpath.css';
link.media = 'all';
head.appendChild(link);

var originalAttributes = new Map();

function getElementByXPath(xpath) {
                    return new XPathEvaluator()
                      .createExpression(xpath)
                      .evaluate(document, XPathResult.FIRST_ORDERED_NODE_TYPE)
                      .singleNodeValue}


function focusItem(item) {
    // removeAttrFromItem(attributes.focused, focusedItem);
    // removeAttrFromItems(attributes.focusedAncestor,
    //     focusedAncestorItems);
    if (!isFocusable(item)) {
        return;
    }
    if (isElementItem(item)) {
        focusedItem = item;
    } else {
        focusedItem = getParentElement(item);
    }
    focusedAncestorItems = getAncestorElements(focusedItem);
    setAttr(attributes.focused, 'true', focusedItem);
    setIndex(attributes.focusedAncestor, focusedAncestorItems);
    focusedItem.blur();
    focusedItem.focus();
    focusedItem.scrollIntoView();
};

function removeAttrFromItem(name, item) {
    if (isElementItem(item)) {
        item.removeAttribute(name);
    }
};

function isElementItem(item) {
    if (isNodeItem(item) && (item.nodeType === Node.ELEMENT_NODE)) {
        return true;
    }
        return false;
};

function isNodeItem (item) {
    if (isAttrItem(item)) {
        return false;
    }
    switch (typeof(item)) {
        case 'string':
        case 'number':
            return false;
        default:
            return true;
        }
};

function isAttrItem(item) {
    return Object.prototype.toString.call(item) === '[object Attr]';
};

function removeAttrFromItems(name, items) {
    items.forEach(item => {
        removeAttrFromItem(name, item);
    });
};

function isFocusable(item) {
    if (!item) {
        return false;
    }
    if (isNodeItem(item) || isAttrItem(item)) {
        return true;
    }
    return false;
};

function getParentElement(item) {
    if (isAttrItem(item)) {
        let parent = item.ownerElement;
        return parent ? parent : null;
    }
    if (isNodeItem(item)) {
        let parent = item.parentElement;
        if (parent) {
            return parent;
        }
        parent = item.parentNode;
        if (parent && (parent.nodeType === Node.ELEMENT_NODE)) {
            return parent;
        }
    }
    return null;
};

function getAncestorElements (elem) {
    var ancs = [];
    var cur = elem;
    var parent = cur.parentElement;
    while (parent) {
        ancs.push(parent);
        cur = parent;
        parent = cur.parentElement;
    }
    parent = cur.parentNode;
    while (parent && (parent.nodeType === Node.ELEMENT_NODE)) {
        ancs.push(cur);
        cur = parent;
        parent = cur.parentNode;
    }
    return ancs;
};

function setAttr(attr, value, item) {
    saveAttrForItem(item, attr, originalAttributes);
    setAttrToItem(attr, value, item);
};

function saveAttrForItem(item, attr, storage, overwrite) {
    storage = storage || new Map();
    if (!isElementItem(item)) {
        return storage;
    }
    var elemStor;
    if (storage.has(item)) {
        elemStor = storage.get(item);
    } else {
        elemStor = new Map();
        storage.set(item, elemStor);
    }
    var val = item.hasAttribute(attr) ? item.getAttribute(attr) :
        null;
    if (overwrite || !elemStor.has(attr)) {
        elemStor.set(attr, val);
    }
    return storage;
};

function setAttrToItem(name, value, item) {
    if (isElementItem(item)) {
        item.setAttribute(name, value);
    }
};

function setIndex(attr, items) {
    saveAttrForItems(items, attr, originalAttributes);
    setIndexToItems(attr, items);
};

function saveAttrForItems(items, attr, storage, overwrite) {
    storage = storage || new Map();
    for (var item of items) {
        saveAttrForItem(item, attr, storage, overwrite);
    }
    return storage;
};

function setIndexToItems(name, items) {
    for (var i = 0; i < items.length; i++) {
        setAttrToItem(name, i, items[i]);
    }
};

var path = getElementByXPath(arguments[0]);
focusItem(path);