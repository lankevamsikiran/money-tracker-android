package com.mymoney.tracker;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceResponse;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.io.ByteArrayOutputStream;

public class MainActivity extends Activity {
    private WebView web;
    private String pendingExport;
    private static final int EXPORT=100, IMPORT=101;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        web=new WebView(this);
        setContentView(web);
        WebSettings settings=web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        web.addJavascriptInterface(new BackupBridge(), "AndroidBackup");
        web.setWebViewClient(new WebViewClient(){
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, String url){
                if(!url.startsWith("https://appassets.androidplatform.net/")) return null;
                try { String name=url.substring("https://appassets.androidplatform.net/".length());
                    if(!name.equals("index.html")&&!name.equals("icon-192.png"))return null;
                    InputStream in=getAssets().open(name);
                    return new WebResourceResponse(name.endsWith("png")?"image/png":"text/html", "UTF-8", in);
                }catch(Exception e){return null;}
            }
        });
        web.loadUrl("https://appassets.androidplatform.net/index.html");
    }
    public class BackupBridge {
        @JavascriptInterface public void exportJson(String json){runOnUiThread(()->{
            pendingExport=json;
            Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");
            i.putExtra(Intent.EXTRA_TITLE,"money-tracker-backup.json");startActivityForResult(i,EXPORT);
        });}
        @JavascriptInterface public void chooseBackup(){runOnUiThread(()->{
            Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");startActivityForResult(i,IMPORT);
        });}
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(result!=RESULT_OK||data==null||data.getData()==null)return;
        Uri uri=data.getData();
        try {
            if(request==EXPORT&&pendingExport!=null){try(OutputStream out=getContentResolver().openOutputStream(uri)){out.write(pendingExport.getBytes(StandardCharsets.UTF_8));}pendingExport=null;}
            if(request==IMPORT){ByteArrayOutputStream bytes=new ByteArrayOutputStream();try(InputStream in=getContentResolver().openInputStream(uri)){byte[] buf=new byte[4096];int n;while((n=in.read(buf))!=-1){if(bytes.size()>5_000_000)throw new Exception("Backup too large");bytes.write(buf,0,n);}}String json=bytes.toString("UTF-8");String encoded=android.util.Base64.encodeToString(json.getBytes(StandardCharsets.UTF_8),android.util.Base64.NO_WRAP);web.evaluateJavascript("window.restoreBackup(decodeURIComponent(escape(atob('"+encoded+"'))))",null);}
        }catch(Exception e){android.widget.Toast.makeText(this,"Backup failed: "+e.getMessage(),android.widget.Toast.LENGTH_LONG).show();}
    }
    @Override public void onBackPressed(){web.evaluateJavascript("if(typeof screen!=='undefined'&&screen!=='home'){nav(screen==='list'?'home':'list')}else{null}",null);}
}
