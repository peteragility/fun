import {cpSync,mkdirSync,copyFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
mkdirSync(path.join(root,'dist'),{recursive:true});
for(const name of ['tongjian','penang-trip']) cpSync(path.join(root,name),path.join(root,'dist',name),{recursive:true});
copyFileSync(path.join(root,'index.html'),path.join(root,'dist/index.html'));
console.log('Built two personal pages.');
