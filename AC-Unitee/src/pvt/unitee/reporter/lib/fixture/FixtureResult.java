package pvt.unitee.reporter.lib.fixture;

import java.util.List;

import com.arjunapro.testauto.interfaces.TestVariables;
import com.google.gson.JsonObject;

import pvt.arjunapro.enums.FixtureResultPropertyType;
import pvt.unitee.reporter.lib.reportable.TestRelatedResult;

public class FixtureResult extends TestRelatedResult{
	FixtureResultProperties resultProps = null;
	
	public FixtureResult(
			FixtureResultProperties resultProps,
			TestVariables testVars) throws Exception{
		super(testVars);
		this.resultProps = resultProps;
	}
	
	public FixtureResultProperties resultProps(){
		return this.resultProps;
	}
	
	public void setExecPoint(String execDesc) throws Exception {
		this.resultProps.setExecPoint(execDesc);
	}

	public void setFixtureMethod(String name) {
		this.resultProps.setFixtureMethod(name);
	}

	public List<String> resultPropStrings(List<FixtureResultPropertyType> props) throws Exception {
		return this.resultProps().strings(props);
	}
	
	public JsonObject asJsonObject() throws Exception{
		JsonObject obj =  new JsonObject();
		FixtureResultSerializer serializer = new FixtureResultSerializer();
		serializer.process(this, obj);
		return obj;
	}
}