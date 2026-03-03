'use strict';



/**
 * add event listener on multiple elements
 */

const addEventOnElements = function (elements, eventType, callback) {
  for (let i = 0, len = elements.length; i < len; i++) {
    elements[i].addEventListener(eventType, callback);
  }
}



/**
 * PRELOADER
 * 
 * preloader will be visible until document load
 */

const preloader = document.querySelector("[data-preloader]");

window.addEventListener("load", function () {
  preloader.classList.add("loaded");
  document.body.classList.add("loaded");
});



/**
 * MOBILE NAVBAR
 * 
 * show the mobile navbar when click menu button
 * and hidden after click menu close button or overlay
 */

const navbar = document.querySelector("[data-navbar]");
const navTogglers = document.querySelectorAll("[data-nav-toggler]");
const overlay = document.querySelector("[data-overlay]");

const toggleNav = function () {
  navbar.classList.toggle("active");
  overlay.classList.toggle("active");
  document.body.classList.toggle("nav-active");
}

addEventOnElements(navTogglers, "click", toggleNav);



/**
 * HEADER & BACK TOP BTN
 * 
 * active header & back top btn when window scroll down to 100px
 */

const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

const activeElementOnScroll = function () {
  if (window.scrollY > 100) {
    header.classList.add("active");
    backTopBtn.classList.add("active");
  } else {
    header.classList.remove("active");
    backTopBtn.classList.remove("active");
  }
}

window.addEventListener("scroll", activeElementOnScroll);



/**
 * SCROLL REVEAL
 */

const revealElements = document.querySelectorAll("[data-reveal]");

const revealElementOnScroll = function () {
  for (let i = 0, len = revealElements.length; i < len; i++) {
    if (revealElements[i].getBoundingClientRect().top < window.innerHeight / 1.15) {
      revealElements[i].classList.add("revealed");
    } else {
      revealElements[i].classList.remove("revealed");
    }
  }
}

window.addEventListener("scroll", revealElementOnScroll);

window.addEventListener("load", revealElementOnScroll);

// ...existing code...

/**
 * ABOUT TAB BUTTONS
 */

const tabBtns = document.querySelectorAll(".tab-btn");
const tabText = document.querySelector(".tab-text");

const tabContents = [
  "ResNet152 is a 152-layer deep residual neural network. Our model fine-tunes the last 3 residual blocks and the fully connected layer on retinal fundus images for DR classification.",
  "Trained on the APTOS 2019 Blindness Detection dataset containing thousands of retinal fundus images labeled by expert clinicians across 5 severity levels.",
  "Team Thiran — A dedicated team of AI researchers and developers building accessible diabetic retinopathy screening tools using deep learning."
];

if (tabBtns.length > 0) {
  addEventOnElements(tabBtns, "click", function () {
    tabBtns.forEach(btn => btn.classList.remove("active"));
    this.classList.add("active");
    const index = [...tabBtns].indexOf(this);
    if (tabText) tabText.textContent = tabContents[index];
  });
}