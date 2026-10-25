package com.alastor.backdrops

import android.app.Activity
import android.os.Bundle
import android.content.Intent
import android.net.Uri
import android.view.View
import android.widget.*
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import java.util.concurrent.Executors

data class Wall(val name:String,val url:String,val category:String)
class MainActivity:Activity() {
 private val pool=Executors.newSingleThreadExecutor()
 private val all=mutableListOf<Wall>()
 private val chosen=mutableSetOf<String>()
 private lateinit var results:LinearLayout
 private lateinit var status:TextView
 private lateinit var query:EditText
 private lateinit var category:Spinner
 private var exportMode="Categories"
 private val base="https://www.backdrops.io/walls/upload/"
 override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState)
  val root=LinearLayout(this).apply { orientation=1; setPadding(20,24,20,12); setBackgroundColor(0xff121018.toInt()) }
  fun button(label:String,action:()->Unit)=Button(this).apply { text=label; setOnClickListener { action() };root.addView(this) }
  fun title(s:String)=TextView(this).apply { text=s; textSize=22f;setTextColor(-1);root.addView(this) }
  title("Backdrops Downloader")
  query=EditText(this).apply { hint="Search filename";setSingleLine();setTextColor(-1);setHintTextColor(0xffaaaaaa.toInt());root.addView(this);addTextChangedListener(object:android.text.TextWatcher {override fun beforeTextChanged(s:CharSequence?,start:Int,count:Int,after:Int){};override fun onTextChanged(s:CharSequence?,start:Int,before:Int,count:Int){render()};override fun afterTextChanged(s:android.text.Editable?){} }) }
  category=Spinner(this);root.addView(category)
  category.onItemSelectedListener=object:android.widget.AdapterView.OnItemSelectedListener {override fun onNothingSelected(p:android.widget.AdapterView<*>?){};override fun onItemSelected(p:android.widget.AdapterView<*>?,v:View?,pos:Int,id:Long){render()} }
  button("Refresh public catalog") { refresh() }
  button("Select visible") { chosen.addAll(filtered().map { it.url });render() }
  button("Clear selection") { chosen.clear();render() }
  button("Export selected originals as ZIP") { export(false) }
  button("Bulk export all visible as ZIP") { export(true) }
  button("Toggle ZIP layout (Categories / Flat)") { exportMode=if(exportMode=="Categories") "Flat" else "Categories";status.text="ZIP layout: $exportMode" }
  status=TextView(this).apply { setTextColor(-1);text="Public catalog not loaded";root.addView(this) }
  val scroll=ScrollView(this);results=LinearLayout(this).apply { orientation=1 };scroll.addView(results);root.addView(scroll,LinearLayout.LayoutParams(-1,0,1f))
  setContentView(root);refresh()
 }
 private fun fetch(url:String):ByteArray { val c=URL(url).openConnection() as HttpURLConnection;c.connectTimeout=15000;c.readTimeout=30000;c.setRequestProperty("User-Agent","BackdropsPublicDownloader/1.0");try {if(c.responseCode !in 200..299) error("HTTP ${c.responseCode}");return c.inputStream.use { it.readBytes() }}finally {c.disconnect()} }
 private fun refresh(){status.text="Loading public image directory…";pool.execute {try {
   val html=fetch(base).toString(Charsets.UTF_8)
   val regex=Regex("href\\s*=\\s*['\"]([^'\"]+)['\"]",RegexOption.IGNORE_CASE)
   val names=regex.findAll(html).mapNotNull { m ->
    val link=m.groupValues[1].replace("&amp;","&")
    val url=URL(URL(base),link).toString()
    val name=Uri.decode(Uri.parse(url).lastPathSegment ?: "")
    if(!url.startsWith(base)||name.startsWith("thumb_",true)||!Regex("(?i)\\.(jpg|jpeg|png|webp|gif|avif)$").containsMatchIn(name)) null
    else Wall(name,url,"Uncategorized")
   }.distinctBy { it.url }.toList()
   runOnUiThread {all.clear();all.addAll(names);updateCategories();status.text="${all.size} public originals found; categories require metadata";render()}
  }catch(e:Exception){runOnUiThread {status.text="Catalog unavailable: ${e.message}"}} }
 }
 private fun updateCategories(){val items=listOf("All")+all.map { it.category }.distinct().sorted();category.adapter=ArrayAdapter(this,android.R.layout.simple_spinner_dropdown_item,items)}
 private fun filtered():List<Wall> {val q=query.text.toString();val c=category.selectedItem?.toString()?:"All";return all.filter {it.name.contains(q,true)&&(c=="All"||it.category==c)} }
 private fun render(){if(!::results.isInitialized)return;results.removeAllViews();val visible=filtered();for(w in visible.take(250)) {
  val check=CheckBox(this).apply {text=w.name;setTextColor(-1);isChecked=w.url in chosen;setOnCheckedChangeListener { _,yes->if(yes)chosen.add(w.url) else chosen.remove(w.url) }};results.addView(check)
 };if(visible.size>250) results.addView(TextView(this).apply {text="Showing first 250 of ${visible.size}; search to narrow"}) }
 private fun export(allVisible:Boolean){val files=if(allVisible) filtered() else all.filter {it.url in chosen};if(files.isEmpty()){status.text="No wallpapers selected";return};pending=files;val intent=Intent(Intent.ACTION_CREATE_DOCUMENT).apply {addCategory(Intent.CATEGORY_OPENABLE);type="application/zip";putExtra(Intent.EXTRA_TITLE,"Backdrops_${if(exportMode=="Categories") "Categories" else "Originals"}.zip")};startActivityForResult(intent,100)}
 private var pending:List<Wall> = emptyList()
 @Deprecated("Activity result") override fun onActivityResult(requestCode:Int,resultCode:Int,data:Intent?){super.onActivityResult(requestCode,resultCode,data);if(requestCode!=100||resultCode!=RESULT_OK)return;val uri=data?.data?:return;val batch=pending.toList();status.text="Exporting ${batch.size} originals…";pool.execute {var ok=0;var failed=0
  try {contentResolver.openOutputStream(uri)?.use {out->ZipOutputStream(out).use {zip->val report=JSONArray();val used=mutableSetOf<String>()
   for((i,w) in batch.withIndex()){try {val bytes=fetch(w.url);val folder=if(exportMode=="Categories") safe(w.category)+"/" else "";var entry=folder+safe(w.name);var suffix=2;while(!used.add(entry)){entry=folder+"${suffix++}_"+safe(w.name)};zip.putNextEntry(ZipEntry(entry));zip.write(bytes);zip.closeEntry();ok++;report.put(JSONObject().put("filename",entry).put("url",w.url).put("category",w.category).put("status","downloaded"))}catch(e:Exception){failed++;report.put(JSONObject().put("url",w.url).put("status","failed").put("error",e.message))};if(i%10==0)runOnUiThread {status.text="Exporting ${i+1}/${batch.size}…"};Thread.sleep(500)}
   zip.putNextEntry(ZipEntry("manifest.json"));zip.write(report.toString(2).toByteArray());zip.closeEntry()
  }};runOnUiThread {status.text="ZIP complete: $ok downloaded, $failed failed"}
  }catch(e:Exception){runOnUiThread {status.text="Export failed: ${e.message}"}} }
 }
 private fun safe(s:String)=s.replace(Regex("[^a-zA-Z0-9._ -]"),"_").take(150).ifBlank {"Unnamed"}
}