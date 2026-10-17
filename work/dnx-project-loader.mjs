import {registerHooks} from 'node:module';
import {existsSync} from 'node:fs';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
const root=resolve('work/upstream/DNX/packages/core/src');
registerHooks({resolve(specifier,context,next){
  if(specifier.startsWith('@noiseandmatter/dnx-core/')) {
    specifier=pathToFileURL(resolve(root,specifier.slice('@noiseandmatter/dnx-core/'.length).replace(/\.js$/,'.ts'))).href;
  } else if(specifier.endsWith('.js') && context.parentURL?.startsWith('file:')) {
    const url=new URL(specifier,context.parentURL);
    if(!existsSync(fileURLToPath(url))) {
      const alt=new URL(url.href.replace(/\.js$/,'.ts'));
      if(existsSync(fileURLToPath(alt)))specifier=alt.href;
    }
  }
  return next(specifier,context);
}});
