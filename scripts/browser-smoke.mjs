import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {withBrowser} from './browser-kit.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../dist');
const blockedStorage = `Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage disabled for review')}});`;
await withBrowser(root,async b=>{
  for(const width of [1440,390,320]) {
    await b.viewport(width,900);
    for(const url of ['/','/tongjian/','/tongjian/volumes/001.html','/tongjian/volumes/294.html','/penang-trip/']) {
      await b.navigate(url,blockedStorage);
      if(url.startsWith('/tongjian/')) await b.waitFor('document.documentElement.dataset.readerReady==="true"');
      assert.ok(await b.evaluate('document.documentElement.scrollWidth<=innerWidth'),url+' overflows at '+width);
      assert.equal(await b.evaluate('document.querySelectorAll("script[src*=analytics]").length'),0);
      if(url.includes('/volumes/')) {
        assert.ok(await b.evaluate('document.querySelector(".juan p").textContent.length>0'));
        assert.ok(await b.evaluate('document.getElementById("readingStatus").textContent.includes("未能保存")'));
        assert.equal(await b.evaluate('document.querySelectorAll("main h1 .title-src a").length'),1);
        assert.equal(await b.evaluate('document.querySelectorAll(".juan .juan-title").length'),0);
      }
      if(url==='/tongjian/') {
        assert.ok(await b.evaluate('document.querySelector(".volume-link").getBoundingClientRect().height<45'),'volume rows stay compact at '+width);
        assert.equal(await b.evaluate('document.querySelectorAll("section.chapter").length'),16);
        assert.ok(await b.evaluate('document.querySelectorAll(".insight").length>=15'));
        assert.equal(await b.evaluate('Array.from(document.querySelectorAll(".spine a")).filter(a=>a.getAttribute("href").startsWith("#ch-")).length'),16);
        assert.ok(await b.evaluate('!!document.getElementById("volumes")'));
        // Fun-redesign checks: TL;DR card, drop cap, sticky position bar.
        assert.equal(await b.evaluate('document.querySelectorAll(".tldr").length'),16);
        assert.equal(await b.evaluate('document.querySelectorAll(".chapter p.body-p .dc").length'),16);
        assert.equal(await b.evaluate('new Set([...document.querySelectorAll(".chapter")].map(c=>getComputedStyle(c).getPropertyValue("--dyn"))).size>=3'),true);
        assert.equal(await b.evaluate('!!document.querySelector(".position-bar")'),true);
      }
    }
  }
  await b.navigate('/');
  assert.equal(await b.evaluate('document.querySelectorAll(".shelf .card").length'),3);
  await b.navigate('/tongjian/');
  assert.equal(await b.evaluate('document.querySelectorAll(".volume-link").length'),294);
  await b.evaluate('const q=document.getElementById("volumeSearch");q.value="唐紀";q.dispatchEvent(new Event("input"))');
  assert.equal(await b.evaluate('document.querySelectorAll(".volume-link:not([hidden])").length'),81);
  await b.navigate('/tongjian/volumes/185.html');
  await b.evaluate('document.getElementById("fontUp").click()');
  assert.equal(await b.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--reading-size").trim()'),'19px');
  await b.navigate('/tongjian/');
  assert.equal(await b.evaluate('document.getElementById("resumeReading").hidden'),false);
  assert.ok(await b.evaluate('document.getElementById("resumeReading").href.includes("185.html")'));
  await b.navigate('/tongjian/#j294');await b.waitFor('location.pathname.endsWith("/294.html")');
  await b.navigate('/penang-trip/');
  assert.equal(await b.evaluate(`document.querySelectorAll('.trip-nav a[href^="#day-"]').length`),6);
  assert.ok(await b.evaluate('document.querySelector(".hero").getBoundingClientRect().height<innerHeight'));
  assert.equal(b.errors.length,0,JSON.stringify(b.errors));
});
console.log('PASS: responsive Fun/reader/travel, blocked storage, 294 volumes, search, resume, font controls and legacy links.');
