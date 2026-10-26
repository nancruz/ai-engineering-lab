"""Numerical reference: real gradient descent and attention, using NumPy only."""
import json
import numpy as np

def sigmoid(z): return 1/(1+np.exp(-np.clip(z,-40,40)))
def loss_grad(w,X,y):
 z=X@w
 loss=np.mean(np.logaddexp(0,z)-y*z)
 return float(loss),X.T@(sigmoid(z)-y)/len(y)

def attention(Q,K,V,mask=None):
 scores=Q@K.T/np.sqrt(Q.shape[1])
 if mask is not None:
  if not np.all(np.any(mask,axis=1)):raise ValueError("every query needs at least one visible key")
  scores=np.where(mask,scores,-np.inf)
 scores=scores-np.max(scores,axis=1,keepdims=True)
 weights=np.exp(scores);weights/=weights.sum(axis=1,keepdims=True)
 return weights@V,weights

def main():
 rng=np.random.default_rng(7)
 X=np.column_stack([np.ones(120),rng.normal(size=(120,3))]);true=np.array([-.2,1.1,-.8,.5])
 y=(rng.random(120)<sigmoid(X@true)).astype(float)
 # Only a numerical mechanics exercise, not a real evidence-gate quality claim.
 train=X[:80];yt=y[:80];test=X[80:];yv=y[80:]
 w=np.array([.1,-.2,.3,.2]);before,grad=loss_grad(w,train,yt);eps=1e-6
 finite=np.zeros_like(w)
 for j in range(len(w)):
  delta=np.zeros_like(w);delta[j]=eps
  finite[j]=(loss_grad(w+delta,train,yt)[0]-loss_grad(w-delta,train,yt)[0])/(2*eps)
 error=float(np.max(np.abs(grad-finite)));assert error<1e-6
 for _ in range(300):w-=.15*loss_grad(w,train,yt)[1]
 after=loss_grad(w,train,yt)[0];assert after<before
 Q=np.array([[1.,0.],[0.,1.]]);K=Q.copy();V=np.array([[2.,1.],[4.,3.]])
 out,weights=attention(Q,K,V,np.tril(np.ones((2,2),dtype=bool)))
 assert np.allclose(weights.sum(axis=1),1);assert weights[0,1]==0;assert np.allclose(out[0],V[0])
 print(json.dumps({"gradient_max_error":error,"train_loss_before":before,"train_loss_after":after,
 "synthetic_test_logloss":loss_grad(w,test,yv)[0],"attention_weights":weights.tolist(),
 "limitations":"Numerical mechanics checks only; neither semantic embeddings nor production model validation."},indent=2))
if __name__=="__main__":main()
