from __future__ import annotations
import queue, threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from titanium import APP_NAME, VERSION, ANDROID_API
from titanium.core import Paths, ConfigStore, ToolchainManager, ANDROID_LICENSE_URL
from titanium.builder import AndroidBuilder

class App:
    def __init__(self,root):
        self.root=root; self.p=Paths(); self.store=ConfigStore(self.p.config); self.q=queue.Queue(); self.t=ToolchainManager(self.p,self.emit); self.b=AndroidBuilder(self.p,self.t,self.emit)
        self.vars={k:tk.StringVar() for k in ["app_name","package","version_name","version_code","min_sdk","target_sdk","source_type","source","output_dir","export_format","build_mode","orientation","keystore","store_password","key_alias","key_password"]}
        self.flags={k:tk.BooleanVar() for k in ["camera","microphone","location","sign_release"]}
        defaults={"app_name":"MyApp","package":"com.swir.myapp","version_name":"1.0.0","version_code":"1","min_sdk":"24","target_sdk":str(ANDROID_API),"source_type":"Folder","output_dir":str(Path.home()/"Desktop"),"export_format":"APK","build_mode":"Debug","orientation":"unspecified"}
        for k,v in defaults.items(): self.vars[k].set(v)
        self.status=tk.StringVar(value="Checking build engine..."); self.ui(); self.load(); root.after(100,self.drain); self.refresh()
    def emit(self,k,t): self.q.put((k,t))
    def drain(self):
        try:
            while True:
                k,t=self.q.get_nowait()
                if k=="status": self.status.set(t)
                else: self.console.config(state="normal"); self.console.insert("end",t+"\n"); self.console.see("end"); self.console.config(state="disabled")
        except queue.Empty: pass
        self.root.after(100,self.drain)
    def ui(self):
        self.root.title(f"{APP_NAME} {VERSION}"); self.root.geometry("1050x760"); outer=ttk.Frame(self.root,padding=14); outer.pack(fill="both",expand=True)
        ttk.Label(outer,text=APP_NAME,font=("Segoe UI",22,"bold")).pack(anchor="w"); ttk.Label(outer,text=f"v{VERSION} • HTML / ZIP / URL → APK / AAB").pack(anchor="w")
        n=ttk.Notebook(outer); n.pack(fill="both",expand=True,pady=10); build=ttk.Frame(n,padding=12); engine=ttk.Frame(n,padding=12); n.add(build,text="Build"); n.add(engine,text="Build Engine")
        form=ttk.Frame(build); form.pack(fill="x")
        fields=[("App name","app_name"),("Package","package"),("Version name","version_name"),("Version code","version_code"),("Min SDK","min_sdk"),("Target SDK","target_sdk")]
        for i,(label,key) in enumerate(fields): r,c=divmod(i,2); ttk.Label(form,text=label).grid(row=r*2,column=c,sticky="w",padx=(0,15)); ttk.Entry(form,textvariable=self.vars[key]).grid(row=r*2+1,column=c,sticky="ew",padx=(0,15),pady=(0,5))
        form.columnconfigure(0,weight=1); form.columnconfigure(1,weight=1)
        s=ttk.LabelFrame(build,text="Web source",padding=8); s.pack(fill="x",pady=8); ttk.Combobox(s,textvariable=self.vars["source_type"],values=["Folder","ZIP","URL"],state="readonly",width=10).pack(side="left"); ttk.Entry(s,textvariable=self.vars["source"]).pack(side="left",fill="x",expand=True,padx=8); ttk.Button(s,text="Browse",command=self.browse_source).pack(side="left")
        o=ttk.LabelFrame(build,text="Build",padding=8); o.pack(fill="x"); ttk.Entry(o,textvariable=self.vars["output_dir"]).grid(row=0,column=0,columnspan=4,sticky="ew"); ttk.Button(o,text="Output",command=self.browse_output).grid(row=0,column=4,padx=5)
        for col,(key,vals) in enumerate([("export_format",["APK","AAB"]),("build_mode",["Debug","Release"]),("orientation",["unspecified","portrait","landscape"])]): ttk.Combobox(o,textvariable=self.vars[key],values=vals,state="readonly",width=14).grid(row=1,column=col,sticky="w",pady=8)
        for col,key in enumerate(["camera","microphone","location"]): ttk.Checkbutton(o,text=key.title(),variable=self.flags[key]).grid(row=2,column=col,sticky="w"); o.columnconfigure(col,weight=1)
        sg=ttk.LabelFrame(build,text="Release signing — passwords are never saved",padding=8); sg.pack(fill="x",pady=8); ttk.Checkbutton(sg,text="Sign release",variable=self.flags["sign_release"]).grid(row=0,column=0,sticky="w"); ttk.Entry(sg,textvariable=self.vars["keystore"]).grid(row=1,column=0,columnspan=3,sticky="ew"); ttk.Button(sg,text="Keystore",command=self.browse_keystore).grid(row=1,column=3,padx=5)
        for col,key in enumerate(["store_password","key_alias","key_password"]): ttk.Entry(sg,textvariable=self.vars[key],show="*" if "password" in key else "").grid(row=2,column=col,sticky="ew",padx=(0,5),pady=5); sg.columnconfigure(col,weight=1)
        ttk.Button(build,text="BUILD APK / AAB",command=self.start_build).pack(fill="x",ipady=7)
        ttk.Label(engine,text="Managed Build Engine",font=("Segoe UI",16,"bold")).pack(anchor="w"); ttk.Label(engine,text="No Android Studio, Python, Node.js or Cordova is required on the target PC.").pack(anchor="w")
        self.engine=tk.Text(engine,height=10,state="disabled",font=("Consolas",10)); self.engine.pack(fill="x",pady=8); row=ttk.Frame(engine); row.pack(fill="x"); ttk.Button(row,text="Refresh",command=self.refresh).pack(side="left"); ttk.Button(row,text="Prepare Build Engine",command=self.prepare).pack(side="left",padx=8); ttk.Label(engine,text=f"Android SDK license: {ANDROID_LICENSE_URL}").pack(anchor="w",pady=8)
        ttk.Label(outer,textvariable=self.status).pack(anchor="w"); self.console=tk.Text(outer,height=9,state="disabled",font=("Consolas",9)); self.console.pack(fill="x")
    def cfg(self):
        d={k:v.get().strip() for k,v in self.vars.items()}; d.update({k:v.get() for k,v in self.flags.items()}); return d
    def load(self):
        c=self.store.load()
        for k,v in self.vars.items():
            if k in c and k not in {"store_password","key_password"}: v.set(c[k])
        for k,v in self.flags.items():
            if k in c: v.set(bool(c[k]))
    def browse_source(self):
        k=self.vars["source_type"].get(); x=filedialog.askdirectory() if k=="Folder" else filedialog.askopenfilename(filetypes=[("ZIP","*.zip")]) if k=="ZIP" else ""
        if x: self.vars["source"].set(x)
    def browse_output(self):
        x=filedialog.askdirectory(); self.vars["output_dir"].set(x or self.vars["output_dir"].get())
    def browse_keystore(self):
        x=filedialog.askopenfilename(filetypes=[("Keystore","*.jks *.keystore"),("All","*.*")]); self.vars["keystore"].set(x or self.vars["keystore"].get())
    def refresh(self):
        text="\n".join(f"{k:22} {v}" for k,v in self.t.status().items()); self.engine.config(state="normal"); self.engine.delete("1.0","end"); self.engine.insert("1.0",text); self.engine.config(state="disabled"); self.status.set("Build engine ready" if self.t.ready() else "Build engine needs preparation")
    def prepare(self):
        if not messagebox.askyesno("Android SDK license","Titanium will download a private JDK, Gradle and Android SDK for this Windows user. Nothing is installed system-wide.\n\nContinue only if you accept the Android SDK license terms."): return
        threading.Thread(target=self._prepare,daemon=True).start()
    def _prepare(self):
        try: self.t.provision(); self.emit("status","Build engine ready")
        except Exception as e: self.emit("log",f"ERROR: {e}"); self.emit("status","Build engine preparation failed")
        self.root.after(0,self.refresh)
    def start_build(self):
        c=self.cfg()
        try: self.b.validate(c)
        except Exception as e: messagebox.showerror("Validation",str(e)); return
        self.store.save(c); self.status.set("Building..."); threading.Thread(target=self._build,args=(c,),daemon=True).start()
    def _build(self,c):
        try:
            out=self.b.build(c); self.emit("log",f"SUCCESS: {out}"); self.emit("status",f"Build complete: {out.name}"); self.root.after(0,lambda:messagebox.showinfo("Titanium",f"Build complete:\n{out}"))
        except Exception as e: self.emit("log",f"ERROR: {e}"); self.emit("status","Build failed"); self.root.after(0,lambda x=str(e):messagebox.showerror("Build failed",x))

if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
